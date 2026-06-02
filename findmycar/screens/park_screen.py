import os
import uuid
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.utils import platform
from kivy.logger import Logger

if platform == "android":
    from android import activity, mActivity
    from android.permissions import request_permissions, Permission


class ParkScreen(Screen):
    storage_service = ObjectProperty(None, allownone=True)
    mapview = ObjectProperty(None, allownone=True)
    locate_button = ObjectProperty(None, allownone=True)
    bottom_nav = ObjectProperty(None, allownone=True)
    address = StringProperty("")
    photo_text = StringProperty("")
    _photo_path = None
    _gps_icon_source = StringProperty("")
    _capture_uri = None
    _photo_dest = None

    def on_pre_enter(self):
        self.storage_service = self.manager.storage_service if hasattr(self.manager, "storage_service") else None

    def on_enter(self):
        self._update_address()
        self._update_gps_icon()

    def _update_address(self):
        if self.storage_service and self.storage_service.last_parking:
            self.address = self.storage_service.last_parking.get("address", "Posizione salvata")
        else:
            self.address = "Nessun parcheggio salvato"

    def _update_gps_icon(self):
        pass

    def take_photo(self):
        if platform != "android":
            self.photo_text = "Solo Android"
            return
        Logger.info("ParkScreen: Requesting camera permission")
        request_permissions(
            [Permission.CAMERA],
            callback=self._on_permission_callback
        )

    def _on_permission_callback(self, permissions, grant_results):
        Logger.info("ParkScreen: Permission result - " + str(permissions) + " -> " + str(grant_results))
        if len(grant_results) > 0 and all(r == 0 for r in grant_results):
            Logger.info("ParkScreen: Permission granted, opening camera")
            Clock.schedule_once(lambda dt: self._open_camera_intent(), 0.1)
        else:
            Logger.warning("ParkScreen: Camera permission denied")
            self.photo_text = "Permesso fotocamera negato"

    def _open_camera_intent(self):
        try:
            from jnius import autoclass, cast
            from android import activity, mActivity

            Intent = autoclass("android.content.Intent")
            MediaStore = autoclass("android.provider.MediaStore")
            ContentValues = autoclass("android.content.ContentValues")

            self._photo_file = "car_" + uuid.uuid4().hex[:8] + ".jpg"
            self._photo_dest = os.path.join(
                os.path.dirname(self.storage_service._file_path),
                self._photo_file,
            )

            values = ContentValues()
            values.put(MediaStore.Images.Media.TITLE, self._photo_file)
            values.put(MediaStore.Images.Media.DISPLAY_NAME, self._photo_file)
            values.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            resolver = mActivity.getContentResolver()
            uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            self._capture_uri = uri

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, uri)
            activity.unbind(on_activity_result=self._on_camera_result)
            activity.bind(on_activity_result=self._on_camera_result)
            mActivity.startActivityForResult(intent, 0x1234)
        except Exception as e:
            Logger.warning("ParkScreen: Camera launch error - " + str(e))
            self.photo_text = "Fotocamera non disponibile"

    def _on_camera_result(self, requestCode, resultCode, intent):
        if requestCode != 0x1234:
            return
        try:
            from android import activity
            activity.unbind(on_activity_result=self._on_camera_result)
        except:
            pass

        if resultCode == -1 and self._capture_uri is not None:
            try:
                from jnius import autoclass

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                mActivity = PythonActivity.mActivity
                resolver = mActivity.getContentResolver()
                Bitmap = autoclass("android.graphics.Bitmap")
                BitmapFactory = autoclass("android.graphics.BitmapFactory")
                FileOutputStream = autoclass("java.io.FileOutputStream")

                istream = resolver.openInputStream(self._capture_uri)
                if istream is not None:
                    bitmap = BitmapFactory.decodeStream(istream)
                    istream.close()
                    if bitmap is not None:
                        fos = FileOutputStream(self._photo_dest)
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                        fos.close()
                        self._photo_path = self._photo_dest
                        self.photo_text = "Foto aggiunta \u2713"
                        return
            except Exception as e:
                Logger.error("ParkScreen: Save error - " + str(e))

        self.photo_text = "Foto non acquisita"

    def on_photo_pressed(self, *args):
        if self._photo_path and os.path.exists(self._photo_path):
            from kivy.uix.image import Image
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button

            layout = BoxLayout(orientation="vertical")
            img = Image(source=self._photo_path, allow_stretch=True, keep_ratio=True)
            close_btn = Button(text="Chiudi", size_hint_y=0.15)
            layout.add_widget(img)
            layout.add_widget(close_btn)

            popup = Popup(title="Foto parcheggio", content=layout, size_hint=(0.9, 0.9), auto_dismiss=True)
            close_btn.bind(on_release=popup.dismiss)
            popup.open()
        else:
            self.take_photo()
