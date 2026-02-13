from ldap3 import Server, Connection, ALL, NTLM
#AD_SERVER = "ldap://dc.10.10.3.63 O 10.10.3.64.local"   # o "ldaps://dc.tudominio.local"
AD_SERVER = "10.10.3.63"   # o "ldaps://dc.tudominio.local"
 
#SERVIENT\inteligencianegocios
DOMAIN = "SERVIENT.COM.CO"
USER = "inteligencianegocios"
PASSWORD = "N3g0c10S3rv13ntr3g4TGB.159yhn753.*-"
 
server = Server(AD_SERVER, get_info=ALL)
 
conn = Connection(
    server,
    user=f"{DOMAIN}\\{USER}",
    password=PASSWORD,
    authentication=NTLM,
    auto_bind=True
)
 
print("Bind OK:", conn.bound)
 