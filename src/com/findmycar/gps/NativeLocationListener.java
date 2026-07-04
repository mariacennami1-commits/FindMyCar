package com.findmycar.gps;

import android.location.Location;
import android.location.LocationListener;
import android.os.Bundle;
import java.util.List;

public class NativeLocationListener implements LocationListener {
    private static volatile double sLatitude;
    private static volatile double sLongitude;
    private static volatile float sAccuracy;
    private static volatile float sBearing;
    private static volatile float sSpeed;
    private static volatile double sAltitude;
    private static volatile long sTime;
    private static volatile boolean sHasFix;
    private static volatile int sStatus;

    public static final int STATUS_UNKNOWN = 0;
    public static final int STATUS_ACTIVE = 1;
    public static final int STATUS_NO_FIX = 2;

    static {
        sStatus = STATUS_UNKNOWN;
    }

    @Override
    public void onLocationChanged(Location location) {
        if (location == null) return;
        sLatitude = location.getLatitude();
        sLongitude = location.getLongitude();
        sAccuracy = location.getAccuracy();
        sBearing = location.getBearing();
        sSpeed = location.getSpeed();
        sAltitude = location.getAltitude();
        sTime = System.currentTimeMillis();
        sHasFix = true;
        sStatus = STATUS_ACTIVE;
    }

    @Override
    public void onLocationChanged(List<Location> locations) {
        if (locations != null && !locations.isEmpty()) {
            onLocationChanged(locations.get(locations.size() - 1));
        }
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
        sStatus = status;
        if (status == 0) {
            sHasFix = false;
        }
    }

    @Override
    public void onProviderEnabled(String provider) {}

    @Override
    public void onProviderDisabled(String provider) {}

    public static double getLatitude() { return sLatitude; }
    public static double getLongitude() { return sLongitude; }
    public static float getAccuracy() { return sAccuracy; }
    public static float getBearing() { return sBearing; }
    public static float getSpeed() { return sSpeed; }
    public static double getAltitude() { return sAltitude; }
    public static long getTime() { return sTime; }
    public static boolean hasFix() { return sHasFix; }
    public static int getStatus() { return sStatus; }
    public static void reset() {
        sHasFix = false;
        sStatus = STATUS_UNKNOWN;
    }
}
