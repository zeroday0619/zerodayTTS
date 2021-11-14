import sqlalchemy

metadata = sqlalchemy.MetaData()

# TTS 지정채널 설정 관련(?)
servers = sqlalchemy.Table(
    "servers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.BigInteger, nullable=False),        # 채널 지정 등록한 user id
    sqlalchemy.Column("guild_id", sqlalchemy.BigInteger, nullable=False, unique=True),       # DISCORD guild id
    sqlalchemy.Column("tts_channel_id", sqlalchemy.BigInteger, nullable=False), # TTS 지정 채널 id
)
