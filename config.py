from decouple import config
class Config:
    SECRET_KEY = "1ʌ@k1.Mtj1k@"

class DevelopmentConfig(Config):
    DEBUG=True
    MYSQL_HOST='localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD=''
    MYSQL_DB='tienda'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587 #puerto de google para TLS: Transport layer security: seguridad de la capa de transporte
    MAIL_USE_TLS = True # se usa protocolo TLS
    MAIL_USERNAME = 'inaxiobitxito@gmail.com' #Nombre de usuario de correo
    MAIL_PASSWORD = config('MAIL_PASSWORD')

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}