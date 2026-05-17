from supabase_client import supabase
   #sign_up
def sign_up(full_name, email, password):
    try:
        # Step 1: Create the user in Supabase auth
        response = supabase.auth.sign_up(credentials={
            "email": email,
            "password": password
        })

        # Step 2: Get the UUID Supabase generated
        user_id = response.user.id

        # Step 3: Save the name into the profiles table
        supabase.table("profiles").insert({
            "user_id": user_id,
            "full_name": full_name,
            "email": email
        }).execute()

        return {"success": True, "user": response.user}

    except Exception as e:
        return {"success": False, "error": str(e)}
   #sign_in 
def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password(credentials={
            "email": email,
            "password": password
        })
        return {"success": True, "user": response.user}

    except Exception as e:
        return {"success": False, "error": str(e)}
#sign_out
def sign_out():
    try:
        supabase.auth.sign_out()
        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
#Forget_password
def reset_password(email):
    try:
        supabase.auth.reset_password_email(email)
        return {"success": True}
    except Exception as e:
        print(f"RESET ERROR: {e}")
        return {"success": False, "error": str(e)}
#update_password
def update_password(new_password):
    try:
        supabase.auth.update_user({"password": new_password})
        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
#update_profile
def update_profile(user_id, full_name, phone, farm_name, location):
    try:
        supabase.table("profiles").update({
            "full_name": full_name,
            "phone": phone,
            "farm_name": farm_name,
            "location": location
        }).eq("user_id", user_id).execute()

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}