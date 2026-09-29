# Índice provisional de la memoria del TFG

1. Introducción
   1.1 Motivación (por qué medir la calidad del agua)
   1.2 Objetivos
   1.3 Alcance y limitaciones
2. Fundamentos
   2.1 Parámetros de calidad del agua: oxígeno disuelto, pH, conductividad, temperatura
   2.2 Comunicaciones LoRa y LoRaWAN (modulación, SF, clases, OTAA)
   2.3 Normativa de la banda de 868 MHz (ETSI EN 300 220, ciclo de trabajo del 1 %)
   2.4 Protocolos usados: RS485/Modbus, I2C, MQTT
3. Diseño del sistema
   3.1 Arquitectura general
   3.2 Nodo de medida (hardware, conexionado, alimentación solar)
   3.3 Red LoRaWAN privada (gateway y ChirpStack)
   3.4 Red de datos: router/NAT, NTP, firewall y acceso remoto
   3.5 Base de datos, web en tiempo real y acceso por DuckDNS
4. Implementación
   4.1 Montaje del nodo
   4.2 Firmware
   4.3 Configuración de la Raspberry y del gateway
   4.4 Servidor de datos
5. Pruebas y resultados
   5.1 Calibración de sondas
   5.2 Cobertura del enlace (RSSI/SNR)
   5.3 Consumo y autonomía
   5.4 Robustez (cortes de red, ingestor parado, Raspberry reiniciada)
6. Presupuesto
7. Conclusiones y mejoras futuras
8. Bibliografía
Anexos: esquemas, código, configuraciones, hojas de datos
