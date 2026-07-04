from kivy.logger import Logger
from kivy.clock import Clock
from jnius import autoclass


class AndroidGPS:
    def __init__(self):
        self._location_manager = None
        self._listener = None
        self._running = False
        self._clock_event = None
        self._on_location_cb = None
        self._on_status_cb = None
        self._provider = None

    def configure(self, on_location=None, on_status=None):
        self._on_location_cb = on_location
        self._on_status_cb = on_status

    def start(self, min_time=1000, min_distance=1):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            Context = autoclass('android.content.Context')
            LocationManager = autoclass('android.location.LocationManager')
            Looper = autoclass('android.os.Looper')

            self._location_manager = activity.getSystemService(
                Context.LOCATION_SERVICE
            )

            NativeLocationListener = autoclass(
                'com.findmycar.gps.NativeLocationListener'
            )
            self._listener = NativeLocationListener()

            criteria = autoclass('android.location.Criteria')()
            criteria.setAccuracy(criteria.ACCURACY_FINE)
            self._provider = self._location_manager.getBestProvider(criteria, True)
            if self._provider is None:
                providers = self._location_manager.getProviders(False)
                for i in range(providers.size()):
                    p = str(providers.get(i))
                    if 'gps' in p.lower():
                        self._provider = p
                        break
                if self._provider is None and providers.size() > 0:
                    self._provider = str(providers.get(0))

            Logger.info('AndroidGPS: Using provider=' + str(self._provider))

            if self._provider:
                self._location_manager.requestLocationUpdates(
                    self._provider,
                    min_time,
                    min_distance,
                    self._listener,
                    Looper.getMainLooper()
                )
                Logger.info('AndroidGPS: requestLocationUpdates called')

            self._running = True
            NativeLocationListener.reset()

            self._last_time = 0
            self._clock_event = Clock.schedule_interval(self._poll, 3)

        except Exception as e:
            Logger.error('AndroidGPS: Failed to start - ' + str(e))
            import traceback
            traceback.print_exc()
            raise

    def _poll(self, dt):
        if not self._running:
            return
        try:
            NativeLocationListener = autoclass(
                'com.findmycar.gps.NativeLocationListener'
            )
            if NativeLocationListener.hasFix():
                t = NativeLocationListener.getTime()
                if t > self._last_time:
                    self._last_time = t
                    kwargs = {
                        'lat': NativeLocationListener.getLatitude(),
                        'lon': NativeLocationListener.getLongitude(),
                        'accuracy': NativeLocationListener.getAccuracy(),
                        'bearing': NativeLocationListener.getBearing(),
                        'speed': NativeLocationListener.getSpeed(),
                        'altitude': NativeLocationListener.getAltitude(),
                    }
                    Logger.info('AndroidGPS: Location ' + str(kwargs['lat']) + ',' + str(kwargs['lon']) + ' acc=' + str(kwargs['accuracy']))
                    if self._on_location_cb:
                        self._on_location_cb(**kwargs)

            status = NativeLocationListener.getStatus()
            if status == 1 and self._on_status_cb:
                self._on_status_cb('gps', 'AVAILABLE')
            elif status == 0 and self._on_status_cb:
                self._on_status_cb('gps', 'OUT_OF_SERVICE')

        except Exception as e:
            Logger.warning('AndroidGPS: Poll error - ' + str(e))

    def stop(self):
        self._running = False
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        if self._location_manager and self._listener:
            try:
                self._location_manager.removeUpdates(self._listener)
            except Exception as e:
                Logger.warning('AndroidGPS: Stop error - ' + str(e))
        Logger.info('AndroidGPS: Stopped')
