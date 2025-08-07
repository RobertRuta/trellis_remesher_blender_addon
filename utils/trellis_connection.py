import concurrent.futures
import bpy
import os
import requests


executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def send_mesh_generation_request_async(props_dict, callback=None):
    def task():
        try:
            result = send_mesh_generation_request(props_dict)
            if callback:
                bpy.app.timers.register(lambda: callback(result), first_interval=0.1)
        except Exception as e:
            print(f"Error in mesh generation: {e}")
            if callback:
                bpy.app.timers.register(lambda: callback(None), first_interval=0.1)

    executor.submit(task)
    

def handle_mesh_generation_result(result):
    if result is None:
        print("Mesh generation failed or was cancelled.")
        return
    mesh_path = result["mesh_path"]
    prompt = result["prompt"]
    mesh_name = prompt.replace(",", "").replace(".", "").replace(" ", "-")
    
    bpy.ops.import_scene.gltf(filepath=mesh_path)
    mesh = bpy.context.selected_objects[0]

    props = bpy.context.scene.auto_remesher
    props.mesh = mesh
    props.mesh.name = mesh_name
    props.mesh["source"] = result["source"]
    props.mesh["prompt_mode"] = result["prompt_mode"]
    props.mesh["prompt"] = prompt

    print("TRELLIS mesh successfully loaded into Blender.")
    

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
    request_dict["generation_quality"] = props_dict["generation_quality"]
    
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

        # Return the imported mesh object
        return {
            "mesh_path": mesh_path,
            "source": result["source"],
            "prompt_mode": result["prompt_mode"],
            "prompt": result["prompt"]
        }
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        raise