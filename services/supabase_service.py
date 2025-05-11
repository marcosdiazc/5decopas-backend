from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def insertar_jugador(data):
    return supabase.table("players").insert(data).execute()

def obtener_jugadores():
    return supabase.table("players").select("*").execute().data

