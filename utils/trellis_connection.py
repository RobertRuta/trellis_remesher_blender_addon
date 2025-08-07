import bpy
import os
import requests


def send_mesh_generation_request(props_dict):
    text_prompt = props_dict["text_prompt"]
    image_prompt = props_dict["image_prompt"]
    
    if len(text_prompt) == 0 and len(image_prompt) == 0:
        raise ValueError("No prompt supplied. Please provide a value for \
                        either \'image_prompt\' or \'text_prompt\'.")
    
    # Validate that exactly one prompt type is provided
    if len(text_prompt) > 0 and len(image_prompt) > 0:
        raise ValueError("Both \'text_prompt\' and \'image_prompt\' \
            provided with valid values. Only one allowed.")
    
    request_dict = {}
    
    # Set final prompt
    if len(text_prompt) > 0:
        prompt = text_prompt
        request_dict["is_text_prompt"] = True
    else:
        prompt = image_prompt
        request_dict["is_text_prompt"] = False
    
    request_dict["prompt"] = prompt
    url = "http://localhost:8765/run_generator"
    
    try:
        response = requests.post(url, json=request_dict)
        response.raise_for_status()
        result = response.json()
        
        if result["status"] != "ok":
            raise RuntimeError("Backend return error.")
    
        mesh_path = result["mesh_path"]
        if not os.path.exists(mesh_path):
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")

        bpy.ops.import_scene.gltf(filepath=mesh_path)

        # Return the imported mesh object
        return {
            "mesh": bpy.context.selected_objects[0],
            "source": result["source"],
            "prompt_mode": result["prompt_mode"],
            "prompt": result["prompt"]
        }
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        raise