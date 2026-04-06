def build_user_systems_response(user_data, all_data) -> list:
    user_systems = []

    for rp in all_data["resourceProviders"]:
        rp_id = rp.get("id")

        if rp_id in user_data:
            user_system_ids = user_data[rp_id]

            systems = [
                {**sys, "rp": rp["name"]}
                for sys in rp.get("systems", [])
                if sys.get("id") in user_system_ids
            ]

            if systems:
                user_systems.extend(systems)
        
    return user_systems


def build_user_resource_providers_response(user_data, all_data) -> list:
    user_resource_providers = []

    for rp in all_data["resourceProviders"]:
        rp_id = rp.get("id")

        if rp_id in user_data:
            rp_data = rp.copy()

            del rp_data["systems"]
            del rp_data["configFields"]

            user_resource_providers.append(rp_data)
        
    return user_resource_providers


def build_user_data_response(user_data, all_data) -> dict:
    user_resource_providers = []
    user_systems = []

    for rp in all_data["resourceProviders"]:
        rp_id = rp.get("id")

        if rp_id in user_data["resourceProviders"]:
            user_system_ids = user_data["systems"][rp_id]

            rp_data = rp.copy()
            del rp_data["systems"]
            del rp_data["configFields"]
            user_resource_providers.append(rp_data)

            systems = [
                {**sys, "rp": rp["name"]}
                for sys in rp.get("systems", [])
                if sys.get("id") in user_system_ids
            ]

            if systems:
                user_systems.extend(systems)

    return {
        "resourceProviders": user_resource_providers,
        "systems": user_systems
    }