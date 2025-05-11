from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def obtener_jugador_por_id(id):
    res = supabase.table("players").select("*").eq("id", id).single().execute()
    return res.data

def actualizar_estadisticas(id, data):
    supabase.table("players").update(data).eq("id", id).execute()


