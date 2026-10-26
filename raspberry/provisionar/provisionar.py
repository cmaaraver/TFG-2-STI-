"""
Provisionar: da de alta en ChirpStack todo lo que antes se hacía a mano (docs/08, paso 6):
contraseña de admin, gateway (wAP LR8), perfil de dispositivo con el codec decoder.js,
aplicación y el nodo con sus claves OTAA. Al final escribe secrets.h para el firmware.

Se lanza desde instalar.sh con  docker compose run --rm provisionar
Se puede repetir sin miedo: lo que ya existe se actualiza con lo del .env, no se duplica.

API gRPC de ChirpStack v4 (paquete chirpstack-api): https://www.chirpstack.io/docs/chirpstack/api/
"""
import logging
import os
import sys
import time

import grpc
from chirpstack_api import api, common
from google.protobuf import empty_pb2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("provisionar")

SERVIDOR = os.environ.get("CHIRPSTACK_SERVIDOR", "chirpstack:8080")
CLAVE_ADMIN = os.environ["CHIRPSTACK_ADMIN_PASSWORD"]
GATEWAY_EUI = os.environ.get("GATEWAY_EUI", "").strip().lower()
DEV_EUI = os.environ["NODO_DEV_EUI"].strip().lower()
JOIN_EUI = os.environ.get("NODO_JOIN_EUI", "0000000000000000").strip().lower()
APP_KEY = os.environ["NODO_APP_KEY"].strip().lower()
NWK_KEY = os.environ["NODO_NWK_KEY"].strip().lower()
CODEC = os.environ.get("CODEC", "/codec/decoder.js")
SALIDA_SECRETS = os.environ.get("SALIDA_SECRETS", "/salida/secrets.h")

NOMBRE_PERFIL = "nodo-agua-eu868"
NOMBRE_APLICACION = "calidad-agua"
NOMBRE_NODO = "nodo-agua"
NOMBRE_GATEWAY = "wap-lr8-azotea"


def comprobar_hex(nombre, valor, cifras):
    if len(valor) != cifras or any(c not in "0123456789abcdef" for c in valor):
        sys.exit(f"ERROR: {nombre} tiene que tener {cifras} cifras hexadecimales (está: '{valor}')")


def conectar():
    # ChirpStack tarda unos segundos en arrancar: se reintenta durante 2 minutos
    canal = grpc.insecure_channel(SERVIDOR)
    for _ in range(60):
        try:
            grpc.channel_ready_future(canal).result(timeout=2)
            return canal
        except grpc.FutureTimeoutError:
            log.info("Esperando a ChirpStack en %s...", SERVIDOR)
            time.sleep(2)
    sys.exit("ERROR: ChirpStack no responde. Mira: docker compose logs chirpstack")


def iniciar_sesion(canal):
    """Entra como admin. La primera vez la contraseña es admin/admin y se cambia por la del .env."""
    interno = api.InternalServiceStub(canal)
    for clave in (CLAVE_ADMIN, "admin"):
        try:
            jwt = interno.Login(api.LoginRequest(email="admin", password=clave)).jwt
        except grpc.RpcError:
            continue
        cabecera = [("authorization", f"Bearer {jwt}")]
        if clave == "admin":
            perfil = interno.Profile(empty_pb2.Empty(), metadata=cabecera)
            api.UserServiceStub(canal).UpdatePassword(
                api.UpdateUserPasswordRequest(user_id=perfil.user.id, password=CLAVE_ADMIN), metadata=cabecera)
            log.info("Contraseña de admin cambiada por la del .env (CHIRPSTACK_ADMIN_PASSWORD)")
        return cabecera
    sys.exit("ERROR: no se puede entrar en ChirpStack ni con la contraseña del .env ni con admin/admin")


def no_existe(error):
    return error.code() == grpc.StatusCode.NOT_FOUND


def primer_tenant(canal, cabecera):
    tenants = api.TenantServiceStub(canal).List(api.ListTenantsRequest(limit=10), metadata=cabecera)
    if not tenants.result:
        sys.exit("ERROR: ChirpStack no tiene ningún tenant")
    return tenants.result[0].id


def alta_gateway(canal, cabecera, tenant_id):
    if not GATEWAY_EUI:
        log.warning("Sin GATEWAY_EUI en el .env: el gateway se da de alta más tarde (README, apartado 4)")
        return
    comprobar_hex("GATEWAY_EUI", GATEWAY_EUI, 16)
    servicio = api.GatewayServiceStub(canal)
    gateway = api.Gateway(gateway_id=GATEWAY_EUI, name=NOMBRE_GATEWAY, tenant_id=tenant_id,
                          description="MikroTik wAP LR8 en el mástil de la azotea", stats_interval=30)
    try:
        # Al actualizar se parte de lo que ya hay en ChirpStack para no borrar campos que no tocamos
        actual = servicio.Get(api.GetGatewayRequest(gateway_id=GATEWAY_EUI), metadata=cabecera).gateway
        actual.MergeFrom(gateway)
        servicio.Update(api.UpdateGatewayRequest(gateway=actual), metadata=cabecera)
        log.info("Gateway %s actualizado", GATEWAY_EUI)
    except grpc.RpcError as e:
        if not no_existe(e):
            raise
        servicio.Create(api.CreateGatewayRequest(gateway=gateway), metadata=cabecera)
        log.info("Gateway %s creado", GATEWAY_EUI)


def alta_perfil(canal, cabecera, tenant_id):
    """Perfil EU868, LoRaWAN 1.1.0, OTAA, clase A, con el codec decoder.js (docs/08, paso 6)."""
    with open(CODEC, encoding="utf-8") as f:
        codigo = f.read()
    servicio = api.DeviceProfileServiceStub(canal)
    perfil = api.DeviceProfile(
        tenant_id=tenant_id, name=NOMBRE_PERFIL, region=common.Region.EU868, region_config_id="eu868",
        mac_version=common.MacVersion.LORAWAN_1_1_0, reg_params_revision=common.RegParamsRevision.RP002_1_0_3,
        adr_algorithm_id="default", supports_otaa=True,
        uplink_interval=15 * 60, device_status_req_interval=1,
        payload_codec_runtime=api.CodecRuntime.JS, payload_codec_script=codigo)
    lista = servicio.List(api.ListDeviceProfilesRequest(tenant_id=tenant_id, search=NOMBRE_PERFIL, limit=10),
                          metadata=cabecera)
    for p in lista.result:
        if p.name == NOMBRE_PERFIL:
            actual = servicio.Get(api.GetDeviceProfileRequest(id=p.id), metadata=cabecera).device_profile
            actual.MergeFrom(perfil)
            servicio.Update(api.UpdateDeviceProfileRequest(device_profile=actual), metadata=cabecera)
            log.info("Perfil %s actualizado (codec incluido)", NOMBRE_PERFIL)
            return p.id
    nuevo = servicio.Create(api.CreateDeviceProfileRequest(device_profile=perfil), metadata=cabecera)
    log.info("Perfil %s creado", NOMBRE_PERFIL)
    return nuevo.id


def alta_aplicacion(canal, cabecera, tenant_id):
    servicio = api.ApplicationServiceStub(canal)
    lista = servicio.List(api.ListApplicationsRequest(tenant_id=tenant_id, search=NOMBRE_APLICACION, limit=10),
                          metadata=cabecera)
    for a in lista.result:
        if a.name == NOMBRE_APLICACION:
            return a.id
    nueva = servicio.Create(api.CreateApplicationRequest(application=api.Application(
        tenant_id=tenant_id, name=NOMBRE_APLICACION, description="Calidad del agua (TFG)")), metadata=cabecera)
    log.info("Aplicación %s creada", NOMBRE_APLICACION)
    return nueva.id


def alta_nodo(canal, cabecera, aplicacion_id, perfil_id):
    servicio = api.DeviceServiceStub(canal)
    nodo = api.Device(dev_eui=DEV_EUI, name=NOMBRE_NODO, application_id=aplicacion_id,
                      device_profile_id=perfil_id, join_eui=JOIN_EUI,
                      description="LILYGO T3 V1.6.1 de la maqueta")
    claves = api.DeviceKeys(dev_eui=DEV_EUI, app_key=APP_KEY, nwk_key=NWK_KEY)
    try:
        actual = servicio.Get(api.GetDeviceRequest(dev_eui=DEV_EUI), metadata=cabecera).device
        actual.MergeFrom(nodo)
        servicio.Update(api.UpdateDeviceRequest(device=actual), metadata=cabecera)
        servicio.UpdateKeys(api.UpdateDeviceKeysRequest(device_keys=claves), metadata=cabecera)
        log.info("Nodo %s actualizado", DEV_EUI)
    except grpc.RpcError as e:
        if not no_existe(e):
            raise
        servicio.Create(api.CreateDeviceRequest(device=nodo), metadata=cabecera)
        servicio.CreateKeys(api.CreateDeviceKeysRequest(device_keys=claves), metadata=cabecera)
        log.info("Nodo %s creado con sus claves OTAA", DEV_EUI)


def bytes_c(clave):
    # "0011..." → "{ 0x00,0x11, ... }" en el mismo orden en que se leen en ChirpStack (MSB primero)
    trozos = [f"0x{clave[i:i + 2]}" for i in range(0, len(clave), 2)]
    grupos = [",".join(trozos[i:i + 4]) for i in range(0, 16, 4)]
    return "{ " + ", ".join(grupos) + " }"


def escribir_secrets():
    texto = f"""#pragma once
// Generado por raspberry/provisionar (docker compose run --rm provisionar). NO se sube a git.
// Mismos datos que el dispositivo "{NOMBRE_NODO}" de ChirpStack. Perfil: EU868, LoRaWAN 1.1.0, OTAA, clase A.

#define LW_JOIN_EUI 0x{JOIN_EUI.upper()}ULL   // JoinEUI
#define LW_DEV_EUI  0x{DEV_EUI.upper()}ULL   // DevEUI del nodo

// Claves de 16 bytes (en ChirpStack: "Application key" y "Network key")
#define LW_APP_KEY {bytes_c(APP_KEY)}
#define LW_NWK_KEY {bytes_c(NWK_KEY)}
"""
    os.makedirs(os.path.dirname(SALIDA_SECRETS), exist_ok=True)
    with open(SALIDA_SECRETS, "w", encoding="utf-8") as f:
        f.write(texto)
    os.chmod(SALIDA_SECRETS, 0o600)
    log.info("Claves del nodo escritas en firmware/nodo-agua/include/secrets.h")


def main():
    comprobar_hex("NODO_DEV_EUI", DEV_EUI, 16)
    comprobar_hex("NODO_JOIN_EUI", JOIN_EUI, 16)
    comprobar_hex("NODO_APP_KEY", APP_KEY, 32)
    comprobar_hex("NODO_NWK_KEY", NWK_KEY, 32)
    canal = conectar()
    cabecera = iniciar_sesion(canal)
    tenant_id = primer_tenant(canal, cabecera)
    alta_gateway(canal, cabecera, tenant_id)
    perfil_id = alta_perfil(canal, cabecera, tenant_id)
    aplicacion_id = alta_aplicacion(canal, cabecera, tenant_id)
    alta_nodo(canal, cabecera, aplicacion_id, perfil_id)
    escribir_secrets()
    log.info("ChirpStack listo")


if __name__ == "__main__":
    main()
