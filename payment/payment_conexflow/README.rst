Pasarela de pago Conexflow. 
===========================

Este módulo añade la opción de pago a través de la pasarela de Conexflow. 
Conexflow es un desarrollo de Informática El Corte Inglés.

Documento: CFPGW-IFZ001-V03 Revisión: 1.26
Informática el Corte Inglés

Parámetros
----------

1 **CF_XtnType**      Tipo de operación solicitada (V-Venta, D-Devolucion, A-anulación, R-devolución referenciada, P-preautorización, C-cofirmación de preautorización)
2 **CF_User**         Código de usuario proporcionado por la plataforma.
3 **CF_Date**         Fecha de la operación. DDMMAAAA
4 **CF_Time**         Hora de la operación. HHMMSS
5 **CF_Amount**       Importe de la operación, expresada en la fracción más pequeña. (Ej. Euros -> se expresa en centimos)
6 **CF_Currency**     Moneda de la operación según ISO 4217
7 **CF_TicketNumber** Referencia de la operación.
7 **CF_Lang**         Lenguaje según ISO 639-1

7 **CF_MAC**          Cálculo del MAC.




