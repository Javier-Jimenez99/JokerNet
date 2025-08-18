"""
Mouse tools for MCP server integration.
"""
import requests
import base64
from fastmcp.utilities.types import Image
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM 
import io
import base64

FASTAPI_URL = "http://localhost:8000"


def get_screen_dimensions() -> dict:
    """
    Get current screen dimensions.
    
    Returns:
        dict: Dictionary containing screen width and height
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/mouse/position", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("screen_size", {"width": 1920, "height": 1080})
        else:
            # Fallback dimensions if request fails
            return {"width": 1920, "height": 1080}
    except Exception:
        # Fallback dimensions if request fails
        return {"width": 1920, "height": 1080}


def mouse_click(x: int, y: int) -> dict:
    """
    Click at a specific coordinate on the screen using pixel coordinates.
    
    Args:
        x (int): X coordinate in pixels
        y (int): Y coordinate in pixels
    
    Returns:
        dict: Status of the click operation
    """
    try:
        payload = {
            "x": x,
            "y": y,
            "button": "left",
            "clicks": clicks
        }
        
        response = requests.post(f"{FASTAPI_URL}/mouse/click", json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> dict:
    """
    Drag the mouse from start coordinates to end coordinates using pixel coordinates.
    
    Args:
        start_x (int): Starting X coordinate in pixels
        start_y (int): Starting Y coordinate in pixels
        end_x (int): Ending X coordinate in pixels
        end_y (int): Ending Y coordinate in pixels
        duration (float): Duration of the drag in seconds (default: 0.5)
        button (str): Mouse button to use for dragging ('left', 'right', 'middle')
    
    Returns:
        dict: Status of the drag operation
    """
    try:
        payload = {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration": duration,
            "button": button
        }
        
        response = requests.post(f"{FASTAPI_URL}/mouse/drag", json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def get_mouse_position() -> dict:
    """
    Get the current mouse position in pixel coordinates.
    
    Returns:
        dict: Dictionary containing pixel coordinates and screen size
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/mouse/position", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def get_screen_with_cursor() -> dict:
    """
    Get a screenshot with the current mouse cursor position highlighted.
    
    Returns:
        dict: Dictionary containing the screenshot with cursor and mouse position
    """
    try:
        # Get the screenshot with cursor
        screenshot_response = requests.get(f"{FASTAPI_URL}/screenshot_with_cursor", timeout=10)

        if screenshot_response.status_code != 200:
            raise RuntimeError(f"Screenshot backend error: HTTP {screenshot_response.status_code} - {screenshot_response.text}")

        # Get the current mouse position
        mouse_pos = get_mouse_position()

        if mouse_pos.get("status") == "error":
            mouse_info = "Error retrieving mouse info"
        elif mouse_pos.get("status") == "success":
            mouse_info = mouse_pos.get("coordinate_info")

        # Convert the image data to base64 for LangChain compatibility
        image_base64 = base64.b64encode(screenshot_response.content).decode('utf-8')

        return {
            "screenshot": f"data:image/png;base64,{image_base64}",
            "mouse_info": mouse_info
        }
        
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to get screenshot with cursor: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")
    
LOCATOR_MODEL = None
LOCATOR_PROCESSOR = None

def locate_element(description: str) -> dict:
    """
    Locate an element on the screen by its description.

    Args:
        description (str): Brief description of the element to locate.

    Returns:
        dict: The location of the element on the screen (if found) or an error message.
    """
    global LOCATOR_MODEL, LOCATOR_PROCESSOR

    try:
        # Initialize model if not already loaded
        if LOCATOR_MODEL is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            # Use explicit cache directory for persistence
            cache_dir = "/root/.cache/huggingface"
            
            # Load model with specific configuration to avoid SDPA issues
            LOCATOR_MODEL = AutoModelForCausalLM.from_pretrained(
                "AskUI/PTA-1", 
                torch_dtype=torch_dtype, 
                trust_remote_code=True,
                cache_dir=cache_dir
            ).to(device)
        
        if LOCATOR_PROCESSOR is None:
            # Use explicit cache directory for persistence
            cache_dir = "/root/.cache/huggingface"
            LOCATOR_PROCESSOR = AutoProcessor.from_pretrained(
                "AskUI/PTA-1", 
                trust_remote_code=True,
                cache_dir=cache_dir
            )

        # Prepare the prompt
        task_prompt = "<OPEN_VOCABULARY_DETECTION>"
        prompt = task_prompt + " " + description

        # Get screenshot
        screenshot_response = requests.get(f"{FASTAPI_URL}/screenshot", timeout=10)
        
        if screenshot_response.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to get screenshot: HTTP {screenshot_response.status_code}"
            }
        
        # Load image
        image = Image.open(io.BytesIO(screenshot_response.content)).convert("RGB")

        # Get device info for tensor operations
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Process inputs
        inputs = LOCATOR_PROCESSOR(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
        # Model and processor are now pre-loaded at startup
        # Generate prediction with additional safety parameters
        generated_ids = LOCATOR_MODEL.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=3,
            use_cache=True,
            pad_token_id=LOCATOR_PROCESSOR.tokenizer.eos_token_id
        )

        # Decode and post-process
        generated_text = LOCATOR_PROCESSOR.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = LOCATOR_PROCESSOR.post_process_generation(
            generated_text, 
            task="<OPEN_VOCABULARY_DETECTION>", 
            image_size=(image.width, image.height)
        )

        # Calculate click position for each detected polygon
        if parsed_answer and '<OPEN_VOCABULARY_DETECTION>' in parsed_answer:
            detection_result = parsed_answer['<OPEN_VOCABULARY_DETECTION>']
            
            # Add click_position for polygons
            if 'polygons' in detection_result and detection_result['polygons']:
                click_positions = []
                for polygon in detection_result['polygons']:
                    if polygon and len(polygon[0]) >= 6:  # At least 3 points (6 coordinates) for a valid polygon
                        # Extract coordinates: [x1, y1, x2, y2, x3, y3, ...]
                        coords = polygon[0]
                        # Calculate center point (centroid)
                        x_coords = [coords[i] for i in range(0, len(coords), 2)]
                        y_coords = [coords[i] for i in range(1, len(coords), 2)]
                        center_x = int(sum(x_coords) / len(x_coords))
                        center_y = int(sum(y_coords) / len(y_coords))
                        click_positions.append({"x": center_x, "y": center_y})
                    else:
                        click_positions.append(None)
                
                detection_result['click_positions'] = click_positions
            
            # Add click_position for bboxes if present
            if 'bboxes' in detection_result and detection_result['bboxes']:
                if 'click_positions' not in detection_result:
                    detection_result['click_positions'] = []
                
                for bbox in detection_result['bboxes']:
                    if bbox and len(bbox) >= 4:  # [x1, y1, x2, y2]
                        center_x = int((bbox[0] + bbox[2]) / 2)
                        center_y = int((bbox[1] + bbox[3]) / 2)
                        detection_result['click_positions'].append({"x": center_x, "y": center_y})
                    else:
                        detection_result['click_positions'].append(None)

        return {
            "status": "success",
            "result": parsed_answer
        }
        
    except Exception as e:
        print(f"Error locating element: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error locating element: {str(e)}"
        }