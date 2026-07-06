import os
import uuid
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.utils import platform
from kivy.lang import Builder
from kivy.logger import Logger

if platform == "android":
    from android import activity, mActivity
    from android.permissions import request_permissions, Permission

Builder.load_string("""
<ParkScreen>:
    canvas.before:
        Color:
            rgba: 0.075, 0.075, 0.082, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Scatta Foto"
            md_bg_color: 0.075, 0.075, 0.082, 1
            specific_text_color: 0.678, 0.776, 1.0, 1
            elevation: 0
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        BoxLayout:
            orientation: "vertical"
            padding: "40dp"
            spacing: "24dp"

            BoxLayout:
                orientation: "vertical"
                spacing: "16dp"
                pos_hint: {"center_y": 0.5}

                MDIcon:
                    icon: "camera"
                    font_size: "80sp"
                    theme_text_color: "Custom"
                    text_color: 0.678, 0.776, 1.0, 1
                    halign: "center"

                MDLabel:
                    text: "Inquadra l'area del parcheggio"
                    font_size: "17sp"
                    theme_text_color: "Custom"
                    text_color: 0.894, 0.886, 0.894, 1
                    halign: "center"

                MDLabel:
                    id: status_label
                    text: root.photo_text
                    font_size: "14sp"
                    theme_text_color: "Custom"
                    text_color: 0.757, 0.776, 0.843, 1
                    halign: "center"

            MDFlatButton:
                id: camera_btn
                text: "APRI FOTOCAMERA"
                icon: "camera"
                font_size: "16sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.894, 0.886, 0.894, 1
                md_bg_color: 0.294, 0.557, 1.0, 1
                radius: [28, 28, 28, 28]
                size_hint_y: None
                height: "56dp"
                on_release: root.take_photo()

            MDFlatButton:
                id: confirm_btn
                text: "CONFERMA"
                icon: "check-circle"
                font_size: "16sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0.18, 0.41, 1
                md_bg_color: 0.325, 0.882, 0.435, 1
                radius: [28, 28, 28, 28]
                size_hint_y: None
                height: "56dp"
                on_release: root.confirm_photo()
""")


class ParkScreen(Screen):
    photo_text = StringProperty("")
    _photo_path = None
    _capture_time_ms = 0
    _callback = None
    _photo_dest = None

    def set_callback(self, callback):
        self._callback = callback

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
        if len(grant_results) > 0 and all(r for r in grant_results):
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
            ContentValues = autoclass("android.content.ContentValues")

            self._photo_file = "car_" + uuid.uuid4().hex[:8] + ".jpg"
            from jnius import autoclass as _ajc
            self._capture_time_ms = _ajc("java.lang.System").currentTimeMillis()
            self._photo_dest = os.path.join(
                mActivity.getFilesDir().getAbsolutePath(),
                self._photo_file,
            )

            photo_uri = None
            try:
                resolver = mActivity.getContentResolver()
                values = ContentValues()
                values.put(MediaStore.Images.Media.DISPLAY_NAME, self._photo_file)
                values.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
                photo_uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            except Exception as e:
                Logger.warning("ParkScreen: MediaStore insert failed: " + str(e))

            self._photo_uri_str = str(photo_uri.toString()) if photo_uri is not None else None
            if self._photo_uri_str:
                Logger.info("ParkScreen: Created MediaStore URI=" + self._photo_uri_str)
            else:
                Logger.info("ParkScreen: No MediaStore URI, using fallback")

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            if photo_uri is not None:
                intent.putExtra(MediaStore.EXTRA_OUTPUT, photo_uri)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                Logger.info("ParkScreen: Intent with EXTRA_OUTPUT")
            else:
                Logger.info("ParkScreen: Intent without EXTRA_OUTPUT")

            activity.unbind(on_activity_result=self._on_camera_result)
            activity.bind(on_activity_result=self._on_camera_result)
            mActivity.startActivityForResult(intent, 0x1234)
            Logger.info("ParkScreen: Camera intent launched, capture_time=" + str(self._capture_time_ms))
        except Exception as e:
            Logger.warning("ParkScreen: Camera launch error - " + str(e))
            import traceback
            Logger.warning("ParkScreen: " + traceback.format_exc())
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
                Uri = autoclass("android.net.Uri")

                # Try reading from our MediaStore URI first (EXTRA_OUTPUT approach)
                uri_str = getattr(self, '_photo_uri_str', None)
                if uri_str:
                    Logger.info("ParkScreen: Trying MediaStore URI=" + uri_str)
                    uri = Uri.parse(uri_str)
                    istream = resolver.openInputStream(uri)
                    if istream is not None:
                        bitmap = BitmapFactory.decodeStream(istream)
                        istream.close()
                        if bitmap is not None:
                            dest = os.path.join(
                                PythonActivity.mActivity.getFilesDir().getAbsolutePath(),
                                self._photo_file,
                            )
                            fos = FileOutputStream(dest)
                            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                            fos.close()
                            self._photo_path = dest
                            self.photo_text = "Foto aggiunta ✓"
                            Logger.info("ParkScreen: Photo saved from MediaStore URI")
                            return

                # Fallback: try thumbnail from intent extras
                extras = intent.getExtras() if intent is not None else None
                Logger.info("ParkScreen: extras=" + str(extras))
                if extras is not None:
                    data = extras.get("data")
                    Logger.info("ParkScreen: extras data=" + str(data))
                    if data is not None:
                        dest = os.path.join(
                            PythonActivity.mActivity.getFilesDir().getAbsolutePath(),
                            self._photo_file,
                        )
                        fos = FileOutputStream(dest)
                        data.compress(Bitmap.CompressFormat.JPEG, 90, fos)
                        fos.close()
                        self._photo_path = dest
                        self.photo_text = "Foto aggiunta ✓"
                        Logger.info("ParkScreen: Photo saved from thumbnail extras")
                        return

                # Fallback: scan MediaStore for recent photo
                Logger.info("ParkScreen: Scanning MediaStore for recent photo")
                time_window_s = 120
                selection = MediaStore.Images.Media.DATE_ADDED + " > " + str(int(self._capture_time_ms / 1000) - time_window_s)
                cursor = resolver.query(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    None,
                    selection,
                    None,
                    MediaStore.Images.Media.DATE_ADDED + " DESC",
                )
                Logger.info("ParkScreen: Cursor(window)=" + str(cursor))
                found = False
                if cursor is not None and cursor.moveToFirst():
                    found = self._copy_from_cursor(cursor, resolver, MediaStore, Bitmap, BitmapFactory, FileOutputStream)
                    cursor.close()
                if not found:
                    Logger.info("ParkScreen: Time-window query returned nothing, trying latest photo")
                    cursor = resolver.query(
                        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                        None,
                        None,
                        None,
                        MediaStore.Images.Media.DATE_ADDED + " DESC",
                    )
                    if cursor is not None and cursor.moveToFirst():
                        found = self._copy_from_cursor(cursor, resolver, MediaStore, Bitmap, BitmapFactory, FileOutputStream)
                        cursor.close()
                if found:
                    return
            except Exception as e:
                Logger.error("ParkScreen: Save error - " + str(e))
                import traceback
                Logger.error("ParkScreen: Traceback - " + str(traceback.format_exc()))

        self.photo_text = "Foto non acquisita"

    def _copy_from_cursor(self, cursor, resolver, MediaStore, Bitmap, BitmapFactory, FileOutputStream):
        try:
            uri_str = cursor.getString(cursor.getColumnIndex("_data"))
            photo_id = cursor.getLong(cursor.getColumnIndex("_id"))
            Logger.info("ParkScreen: Found photo _id=" + str(photo_id) + " path=" + str(uri_str))
            uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI.buildUpon().appendPath(
                str(photo_id)
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
                    return True
        except Exception as e:
            Logger.error("ParkScreen: _copy_from_cursor error - " + str(e))
        return False

    def confirm_photo(self):
        if self._callback and self._photo_path:
            cb = self._callback
            self._callback = None
            cb(self._photo_path)
        else:
            self.go_back()

    def go_back(self):
        if self._callback:
            cb = self._callback
            self._callback = None
            cb(None)
        else:
            self.manager.current = "home"
