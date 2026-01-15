# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
import imgkit
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
from typing import List, Dict, Any
from parsers.base_parser import Conversation, Message # Assuming this path is correct

class AnimatedGifGenerator:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        # Define some basic styling for the bubbles
        # These would ideally be more sophisticated or use CSS files
        self.style = """
        <style>
            body { font-family: sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; display: flex; flex-direction: column; }
            .message-bubble {
                border-radius: 15px;
                padding: 10px 15px;
                margin: 5px 10px;
                max-width: 70%;
                word-wrap: break-word;
                box-shadow: 0 1px 1px rgba(0,0,0,0.1);
            }
            .user-message .message-bubble {
                background-color: #007AFF; color: white; align-self: flex-end;
                border-bottom-right-radius: 5px;
            }
            .assistant-message .message-bubble {
                background-color: #e5e5ea; color: black; align-self: flex-start;
                border-bottom-left-radius: 5px;
            }
            .sender { font-weight: bold; margin-bottom: 3px; font-size: 0.8em; }
            .content { font-size: 1em; }
            .timestamp { font-size: 0.7em; color: #888; text-align: right; margin-top: 5px; }
            /* Basic styles for a "typing" indicator */
            .typing-indicator {
                display: flex;
                align-items: center;
                padding: 10px;
            }
            .typing-dot {
                width: 8px;
                height: 8px;
                background-color: #aaa;
                border-radius: 50%;
                margin: 0 2px;
                animation: typing 1s infinite ease-in-out;
            }
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
        </style>
        """
        self.frame_width = 400  # Width of the GIF frames
        self.frame_height_padding = 20 # Padding for auto-height calculation

    def _get_bubble_html(self, message: Message) -> str:
        role = message.role.lower()
        # Basic HTML structure for a single bubble
        content_html = message.content.replace("\n", "<br>")
        html = f"""
        <html><head>{self.style}</head><body>
        <div class="{role}-message" style="display: flex; flex-direction: column;">
            <div class="message-bubble">
                <div class="sender">{message.role.title()}</div>
                <div class="content">{content_html}</div>
            </div>
        </div>
        </body></html>
        """
        return html

    def _get_typing_indicator_html(self) -> str:
        return f"""
        <html><head>{self.style}</head><body>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        </body></html>
        """

    def _html_to_image(self, html_content: str, output_path: str, width: int) -> bool:
        try:
            options = {'width': width, 'disable-smart-width': '', 'quiet': ''}
            imgkit.from_string(html_content, output_path, options=options)
            # Auto-crop image to content height (simple version)
            img = Image.open(output_path)

            # Find bounding box of non-background pixels
            # Convert to grayscale and find non-background (assuming background is light)
            # This is a common way to find the content box.
            # If the background is transparent or varies, this needs adjustment.
            # Forcing a white background for consistent cropping.
            bg = Image.new("RGB", img.size, (240, 240, 240)) # Match body background-color
            bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None) # Handle transparency

            # Find bounding box of non-background pixels
            # Convert to grayscale and find non-white pixels
            gray_img = bg.convert('L')
            non_bg_pixels = []
            for x in range(gray_img.width):
                for y in range(gray_img.height):
                    if gray_img.getpixel((x,y)) < 235: # Threshold for non-background
                        non_bg_pixels.append((x,y))

            if not non_bg_pixels: # Empty image or all background
                # Fallback: save a small default height if no content found
                img = img.crop((0, 0, width, 50))
                img.save(output_path)
                return True

            min_x = min(p[0] for p in non_bg_pixels)
            max_x = max(p[0] for p in non_bg_pixels)
            min_y = min(p[1] for p in non_bg_pixels)
            max_y = max(p[1] for p in non_bg_pixels)

            # Add some padding to the height
            cropped_img = img.crop((0, min_y, width, max_y + self.frame_height_padding))
            cropped_img.save(output_path)

            return True
        except Exception as e:
            print(f"Error converting HTML to image: {e}")
            # Check if wkhtmltoimage is found
            if "No such file or directory: 'wkhtmltoimage'" in str(e):
                print("wkhtmltoimage not found. Please ensure it is installed and in your PATH.")
            return False

    def generate_gif(self, conversation: Conversation, output_gif_path: str, frame_duration: int = 1500, typing_duration: int = 1000, typing_frames: int = 3) -> bool:
        frames = []
        temp_dir = tempfile.mkdtemp()

        try:
            # Initial blank frame or title frame (optional)
            # For now, directly start with messages

            for i, message in enumerate(conversation.messages):
                # Create image for the message bubble
                bubble_html = self._get_bubble_html(message)
                frame_path = os.path.join(temp_dir, f"frame_{i}_msg.png")
                if self._html_to_image(bubble_html, frame_path, self.frame_width):
                    frames.append(Image.open(frame_path))
                else:
                    print(f"Could not generate frame for message {i}")
                    continue # Skip this frame

                # Add typing indicator frames before the next message (if it's from assistant)
                if i < len(conversation.messages) - 1:
                    # Simple: add typing indicator if next is assistant, or after user.
                    # More complex: only if current is user and next is assistant.
                    # Let's assume typing before every message for now, for simplicity of demo
                    typing_html = self._get_typing_indicator_html()
                    typing_frame_path = os.path.join(temp_dir, f"frame_{i}_typing.png")
                    if self._html_to_image(typing_html, typing_frame_path, self.frame_width):
                        # Adjust typing indicator image height
                        typing_img = Image.open(typing_frame_path)
                        # A fixed height for typing indicator might be better
                        fixed_height_typing = 70
                        typing_img = typing_img.crop((0,0, self.frame_width, min(typing_img.height, fixed_height_typing)))

                        # Add multiple frames for animation effect if Pillow handles duration per frame well,
                        # otherwise, we make the single frame last longer.
                        # Pillow's save() takes a duration for all frames, or list of durations.
                        # For simplicity, one typing frame image, its duration controlled later.
                        frames.append(typing_img)
                    else:
                        print(f"Could not generate typing frame after message {i}")

            # The 'frames' list now contains a sequence of message images and typing indicator images.
            # The logic below rebuilds this into 'processed_frames' and 'frame_durations'
            # with specific durations for each type. The original 'frames' list is not directly used for saving.

            # Rebuild frames list with explicit typing indicators
            # (This section correctly assigns durations based on message vs typing)
            processed_frames = []
            frame_durations = []

            for i, message in enumerate(conversation.messages):
                bubble_html = self._get_bubble_html(message)
                frame_path = os.path.join(temp_dir, f"msg_frame_{i}.png")
                if self._html_to_image(bubble_html, frame_path, self.frame_width):
                    processed_frames.append(Image.open(frame_path))
                    frame_durations.append(frame_duration) # Duration for message
                else:
                    print(f"Skipping frame for message {i}")
                    continue

                # Add typing indicator before the next message, but not after the last one
                if i < len(conversation.messages) - 1:
                    typing_html = self._get_typing_indicator_html()
                    typing_frame_path = os.path.join(temp_dir, f"typing_frame_{i}.png")
                    if self._html_to_image(typing_html, typing_frame_path, self.frame_width):
                        typing_img = Image.open(typing_frame_path)
                        fixed_height_typing = 70
                        cropped_typing_img = typing_img.crop((0,0, self.frame_width, min(typing_img.height, fixed_height_typing)))

                        # Add multiple, short-duration frames for the "animation" of typing indicator
                        for _ in range(typing_frames):
                            processed_frames.append(cropped_typing_img)
                            frame_durations.append(typing_duration // typing_frames)
                    else:
                        print(f"Skipping typing frame after message {i}")

            if not processed_frames:
                print("No frames processed, cannot create GIF.")
                return False

            # Save frames as animated GIF
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)

            processed_frames[0].save(
                output_gif_path,
                save_all=True,
                append_images=processed_frames[1:],
                duration=frame_durations, # list of durations for each frame
                loop=0,  # Loop indefinitely
                optimize=True
            )
            print(f"Animated GIF saved to {output_gif_path}")
            return True

        except Exception as e:
            print(f"Error generating GIF: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up temporary image files
            if os.path.exists(temp_dir):
                for f_name in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, f_name))
                os.rmdir(temp_dir)
            print(f"Cleaned up temp directory: {temp_dir}")

# Example Usage (for testing this script directly)
if __name__ == '__main__':
    from datetime import datetime # Ensure datetime is imported for MockConversation

    # Mock Conversation and Message objects for testing
    class MockMessage(Message):
        def __init__(self, role: str, content: str, timestamp: Any = None, uuid: str = None): # Added uuid for completeness
            super().__init__(role=role, content=content, timestamp=timestamp, uuid=uuid)

    class MockConversation(Conversation):
        def __init__(self, title: str, messages: List[Message], source: str = "test_source", id: str = "test_conv_id", uuid: str = None):
            # created_at is mandatory for the base Conversation class
            super().__init__(title=title, messages=messages, source=source, id=id, uuid=uuid, created_at=datetime.now(), updated_at=None)

    print("Starting GIF generator test...")
    # Create a dummy assets directory if it doesn't exist for the test
    if not os.path.exists("scripts/assets"):
        os.makedirs("scripts/assets")

    gif_gen = AnimatedGifGenerator(assets_dir='scripts/assets') # assets_dir is not used yet in this basic version

    test_messages = [
        MockMessage(role="user", content="Hello! This is a test message."),
        MockMessage(role="assistant", content="Hi there! This is a response. It might be a bit longer to see how text wrapping works."),
        MockMessage(role="user", content="Great! How about special characters? & < > \" '"),
        MockMessage(role="assistant", content="Special characters like &amp; &lt; &gt; &quot; ' should be handled by imgkit if rendered as HTML entities or escaped properly in the HTML string. This test doesn't explicitly do that yet for content, relying on browser engine via imgkit."),
        MockMessage(role="user", content="Let's make this one final message to check the sequence.")
    ]
    test_conversation = MockConversation(title="Test GIF Conversation", messages=test_messages)

    output_directory = "data/gifs" # Ensure this directory exists or is created by generate_gif
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, "test_conversation.gif")

    success = gif_gen.generate_gif(test_conversation, output_path)

    if success:
        print(f"Test GIF generated successfully: {output_path}")
    else:
        print("Test GIF generation failed.")

    # Test with an empty conversation
    empty_conversation = MockConversation(title="Empty Test", messages=[])
    empty_output_path = os.path.join(output_directory, "empty_test.gif")
    success_empty = gif_gen.generate_gif(empty_conversation, empty_output_path)
    if not success_empty:
        print("Empty conversation test correctly reported failure or no GIF.")
    else:
        print(f"Empty conversation test unexpectedly created a GIF: {empty_output_path}")
