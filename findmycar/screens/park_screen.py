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
            from jnius import autoclass
            from android import activity, mActivity

            Intent = autoclass("android.content.Intent")
            MediaStore = autoclass("android.provider.MediaStore")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            self._photo_file = "car_" + uuid.uuid4().hex[:8] + ".jpg"
            self._photo_dest = os.path.join(
                PythonActivity.mActivity.getFilesDir().getAbsolutePath(),
                self._photo_file,
            )
            from jnius import autoclass as _ajc
            self._capture_time_ms = _ajc("java.lang.System").currentTimeMillis()

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            activity.unbind(on_activity_result=self._on_camera_result)
            activity.bind(on_activity_result=self._on_camera_result)
            mActivity.startActivityForResult(intent, 0x1234)
            Logger.info("ParkScreen: Camera intent launched, capture_time=" + str(self._capture_time_ms))
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

        Logger.info("ParkScreen: Camera result - code=" + str(resultCode) + " intent=" + str(intent))

        if resultCode == -1:
            try:
                from jnius import autoclass

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                mActivity = PythonActivity.mActivity
                resolver = mActivity.getContentResolver()
                MediaStore = autoclass("android.provider.MediaStore")
                Bitmap = autoclass("android.graphics.Bitmap")
                BitmapFactory = autoclass("android.graphics.BitmapFactory")
                FileOutputStream = autoclass("java.io.FileOutputStream")

                extras = intent.getExtras() if intent is not None else None
                Logger.info("ParkScreen: extras=" + str(extras))
                if extras is not None:
                    data = extras.get("data")
                    Logger.info("ParkScreen: extras data=" + str(data))
                    if data is not None:
                        bitmap = data
                        fos = FileOutputStream(self._photo_dest)
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                        fos.close()
                        self._photo_path = self._photo_dest
                        self.photo_text = "Foto aggiunta ✓"
                        Logger.info("ParkScreen: Photo saved from thumbnail extras")
                        return

                if intent is not None and intent.getData() is not None:
                    uri = intent.getData()
                    Logger.info("ParkScreen: Got URI from intent data=" + str(uri))
                    istream = resolver.openInputStream(uri)
                    if istream is not None:
                        bitmap = BitmapFactory.decodeStream(istream)
                        istream.close()
                        if bitmap is not None:
                            fos = FileOutputStream(self._photo_dest)
                            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                            fos.close()
                            self._photo_path = self._photo_dest
                            self.photo_text = "Foto aggiunta ✓"
                            Logger.info("ParkScreen: Photo saved from intent data URI")
                            return

                Logger.info("ParkScreen: Scanning MediaStore for recent photo")
                cursor = resolver.query(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    None,
                    MediaStore.Images.Media.DATE_ADDED + " > " + str(int(self._capture_time_ms / 1000) - 5),
                    None,
                    MediaStore.Images.Media.DATE_ADDED + " DESC",
                )
                Logger.info("ParkScreen: Cursor=" + str(cursor))
                if cursor is not None and cursor.moveToFirst():
                    uri_str = cursor.getString(cursor.getColumnIndex("_data"))
                    Logger.info("ParkScreen: Found gallery photo at " + str(uri_str))
                    if uri_str:
                        uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI.buildUpon().appendPath(
                            str(cursor.getLong(cursor.getColumnIndex("_id")))
                        ).build()
                        istream = resolver.openInputStream(uri)
                        if istream is not None:
                            bitmap = BitmapFactory.decodeStream(istream)
                            istream.close()
                            if bitmap is not None:
                                fos = FileOutputStream(self._photo_dest)
                                bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                                fos.close()
                                self._photo_path = self._photo_dest
                                self.photo_text = "Foto aggiunta ✓"
                                Logger.info("ParkScreen: Photo saved from gallery scan")
                                return
                    cursor.close()
            except Exception as e:
                Logger.error("ParkScreen: Save error - " + str(e))
                import traceback
                Logger.error("ParkScreen: Traceback - " + str(traceback.format_exc()))

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
