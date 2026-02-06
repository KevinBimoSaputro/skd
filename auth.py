from database import supabase

def login(nama, password):
    result = supabase.table("users") \
        .select("*") \
        .eq("nama", nama) \
        .eq("password", password) \
        .execute()

    if result.data:
        return result.data[0]
    else:
        return None
