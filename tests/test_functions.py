import numpy as np
import pytest
import ACSE9.SolarModel as SolarModel


class TestFunctions(object):
    """
    Class for testing (by validation) the functions
    associated with the modules within the ACSE9 package.
    """
    foo = 'n, min_dec, max_dec, jan_end,'
    foo = foo + 'june_start, june_end, december_start'

    @pytest.mark.parametrize(foo, [
                              ((np.linspace(1, 365, 365)),
                               -23.45,
                               23.45,
                               31, 152, 182, 335
                               )])
    def test_solar_declination(self, n, min_dec, max_dec,
                               jan_end,
                               june_start, june_end,
                               december_start):
        """
        Test the solar declination function in
        ACSE9.SolarModel.SolarArray:

        Solar declination should vary sinusoidally between the limits of
        -23.45 degrees and 23.45 degrees, reaching a peak in June and a
        minimum in January and December (Duffie and Beckman, 2002).
        """
        # define dummy SolarArray class object
        time_zone = 0.0
        lat = 0.0
        long = 0.0
        slope = 0.0
        azimuth = 0.0
        dt = 0.0
        Module_Capacity = 0.0
        Module_Count = 0
        albedo = 0.0
        Derating_Factor = 0.0

        # initialise solar model in a SolarArray class
        dummy = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                      Module_Capacity, Module_Count, albedo,
                                      Derating_Factor)
        test = np.zeros(len(n))  # array to store test data
        for i in range(len(n)):
            day = int(n[i])
            # run solar declination class method
            dummy.Calculate_Solar_Declination(day)
            # store result
            test[i] = dummy.Solar_Declination

        # test that the minimums and maximums are the correct values
        min_test = np.round(min(test), 2)
        max_test = np.round(max(test), 2)
        assert np.isclose(min_test, min_dec)
        assert np.isclose(max_test, max_dec)
        # check that the minimums and maximums occur in jan/dec and june
        min_dates = np.where(test < -23.0)[0]  # dates where minimums occur
        jan_test = min_dates <= jan_end
        december_test = min_dates >= december_start
        jan_december_test = jan_test | december_test
        assert np.all(jan_december_test)
        max_dates = np.where(test > 23.0)[0]  # dates where maximums occur
        june_start_test = max_dates >= june_start
        june_end_test = max_dates <= june_end
        june_test = june_start_test | june_end_test
        assert np.all(june_test)

    foo = 'n1, t_c1, tz_1, long1, st1, '
    foo = foo + 'n2, t_c2, tz_2, long2, st2, '
    foo = foo + 'n3, t_c3, tz_3, long3, st3'

    @pytest.mark.parametrize(foo, [
                              (102, 14.75, 0.0, -0.161920, 14.72,
                               88, 22.13, 8.0, 114.058172, 21.64,
                               34, 10.5, -5.0, -89.393153, 9.32
                               )])
    def test_solar_time(self, n1, t_c1, tz_1, long1, st1,
                        n2, t_c2, tz_2, long2, st2,
                        n3, t_c3, tz_3, long3, st3):

        """
        Test the solar time function in
        ACSE9.SolarModel.SolarArray:

        Some results for solar time were generated using the solar calculator
        provided by geoastro.de
        (http://www.geoastro.de/astro/suncalc/index.htm),
        using calculations from the
        National Oceanic and Atmospheric Administration (NOAA):

        Result 1
        --------
        Inputs: Longitude = -0.161920; Time-zone (±GMT) = 0;
        Local time = 14.75 (14:45); Day-of-year = 102
        Expected output: Solar time = 14.72 (14:43)

        Result 2
        --------
        Inputs: Longitude = 114.058172; Time-zone (±GMT) = +8;
        Local time = 22.13 (22:08); Day-of-year = 88
        Expected output: Solar time = 21.64 (21:39)

        Result 3
        --------
        Inputs: Longitude = -89.393153; Time-zone (±GMT) = -5;
        Local time = 10.50 (10:30); Day-of-year = 34
        Expected output: Solar time = 9.32

        NOTE: A slight rounding discrepancy will be accepted for validation,
        as it is not clear what rounding accuracy geoastro.de uses.
        """
        # define dummy SolarArray class object
        lat = 0.0
        slope = 0.0
        azimuth = 0.0
        dt = 0.0
        Module_Capacity = 0.0
        Module_Count = 0
        albedo = 0.0
        Derating_Factor = 0.0

        time_zone = tz_1  # The time zone in hours east of GMT.
        long = long1   # The longitude of the Solar PV facility, degrees.
        # initialise solar model in a SolarArray class
        dummy = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                      Module_Capacity, Module_Count, albedo,
                                      Derating_Factor)
        # run solar time class method
        dummy.Calculate_Solar_Time(n1, t_c1)
        # store result
        test = dummy.Solar_Time
        assert np.allclose(np.round(test, 1), np.round(st1, 1))

        # second test case:
        dummy.time_zone = tz_2  # The time zone in hours east of GMT.
        dummy.long = long2   # The longitude of the Solar PV facility, degrees.
        # run solar time class method
        dummy.Calculate_Solar_Time(n2, t_c2)
        # store result
        test = dummy.Solar_Time
        assert np.allclose(np.round(test, 1), np.round(st2, 1))

        # third test case:
        dummy.time_zone = tz_3  # The time zone in hours east of GMT.
        dummy.long = long3   # The longitude of the Solar PV facility, degrees
        # run solar time class method
        dummy.Calculate_Solar_Time(n3, t_c3)
        # store result
        test = dummy.Solar_Time
        assert np.allclose(np.round(test, 1), np.round(st3, 1))

    foo = 'n1, t_c1, tz_1, long1, ha1, '
    foo = foo + 'n2, t_c2, tz_2, long2, ha2, '
    foo = foo + 'n3, t_c3, tz_3, long3, ha3'

    @pytest.mark.parametrize(foo, [
                              (102, 14.75, 0.0, -0.161920, 40.83,
                               88, 22.13, 8.0, 114.058172, 144.73,
                               34, 10.5, -5.0, -89.393153, -40.26
                               )])
    def test_hour_angle(self, n1, t_c1, tz_1, long1, ha1,
                        n2, t_c2, tz_2, long2, ha2,
                        n3, t_c3, tz_3, long3, ha3):

        """
        Test the hour angle function in
        ACSE9.SolarModel.SolarArray:

        Some results for solar time were generated using the
        solar time calculatorprovided by PVEducation.org
        (https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time):

        Result 1
        --------
        Inputs: Longitude = -0.161920; Time-zone (±GMT) = 0;
        Local time = 14.75 (14:45); Day-of-year = 102
        Expected output: Hour angle = 40.83 degrees

        Result 2
        --------
        Inputs: Longitude = 114.058172; Time-zone (±GMT) = +8;
        Local time = 22.13 (22:08); Day-of-year = 88
        Expected output: Hour angle = 144.73 degrees

        Result 3
        --------
        Inputs: Longitude = -89.393153; Time-zone (±GMT) = -5;
        Local time = 10.50 (10:30); Day-of-year = 34
        Expected output: Hour angle = -40.25 degrees

        NOTE: A slight rounding discrepancy will be accepted for validation,
        as it is not clear what rounding accuracy geoastro.de uses.
        """
        # define dummy SolarArray class object
        lat = 0.0
        slope = 0.0
        azimuth = 0.0
        dt = 0.0
        Module_Capacity = 0.0
        Module_Count = 0
        albedo = 0.0
        Derating_Factor = 0.0

        time_zone = tz_1  # The time zone in hours east of GMT.
        long = long1   # The longitude of the Solar PV facility, in degrees.
        # initialise solar model in a SolarArray class
        dummy = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                      Module_Capacity, Module_Count, albedo,
                                      Derating_Factor)
        # run solar time class method
        dummy.Calculate_Solar_Time(n1, t_c1)
        # run hour angle class method
        dummy.Calculate_Hour_Angle()
        # store result
        test = dummy.Hour_Angle
        assert np.allclose(np.round(test, 1), np.round(ha1, 1))

        # second test case:
        dummy.time_zone = tz_2
        dummy.long = long2
        dummy.Calculate_Solar_Time(n2, t_c2)
        dummy.Calculate_Hour_Angle()
        test = dummy.Hour_Angle
        assert np.allclose(np.round(test, 1), np.round(ha2, 1))

        # third test case:
        dummy.time_zone = tz_3
        dummy.long = long3
        dummy.Calculate_Solar_Time(n3, t_c3)
        dummy.Calculate_Hour_Angle()
        test = dummy.Hour_Angle
        assert np.allclose(np.round(test, 1), np.round(ha3, 1))

    foo = 'n, min_enr, max_enr, jan_end,'
    foo = foo + 'june_start, june_end, december_start'

    @pytest.mark.parametrize(foo, [
                              ((np.linspace(1, 365, 365)),
                               1.32,
                               1.41,
                               31, 152, 182, 335
                               )])
    def test_extraterrestrial_normal(self, n, min_enr, max_enr,
                                     jan_end,
                                     june_start, june_end,
                                     december_start):
        """
        Test the extraterrestrial normal radiation
        function in ACSE9.SolarModel.SolarArray:

        Duffie and Beckman (2002) note that extraterrestrial
        normal radiation varies sinusoidally with respect to the
        day of the year, with a peak of arround 1.41 kW/m^2 in
        January and December and a minimum of around 1.32 kW/m^2
        in June (Figure 1.4.1).
        """
        # define dummy SolarArray class object
        time_zone = 0.0
        lat = 0.0
        long = 0.0
        slope = 0.0
        azimuth = 0.0
        dt = 0.0
        Module_Capacity = 0.0
        Module_Count = 0
        albedo = 0.0
        Derating_Factor = 0.0

        # initialise solar model in a SolarArray class
        dummy = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                      Module_Capacity, Module_Count, albedo,
                                      Derating_Factor)
        test = np.zeros(len(n))  # array to store test data
        for i in range(len(n)):
            day = int(n[i])
            # run solar declination class method
            dummy.Calculate_Extraterrestrial_Normal_Radiation(day)
            # store result
            test[i] = dummy.Extraterrestrial_Normal_Radiation

        # test that the minimums and maximums are the correct values
        min_test = np.round(min(test), 2)
        max_test = np.round(max(test), 2)
        assert np.isclose(min_test, min_enr)
        assert np.isclose(max_test, max_enr)
        # check that the minimums and maximums occur in june and jan/dec
        min_dates = np.where(test < 1.339)[0]  # dates where minimums occur
        june_start_test = min_dates >= june_start
        june_end_test = min_dates <= june_end
        june_test = june_start_test | june_end_test
        assert np.all(june_test)
        max_dates = np.where(test > 1.409)[0]  # dates where maximums occur
        jan_test = max_dates <= jan_end
        december_test = max_dates >= december_start
        jan_december_test = jan_test | december_test
        assert np.all(jan_december_test)

    foo = 'lat, slope, azimuth, dec, ha, aoi'

    @pytest.mark.parametrize(foo, [
                              (43.0,
                               45.0,
                               15.0,
                               -14.0,
                               -22.5,
                               35.0
                               )])
    def test_angle_of_incidence(self, lat, slope, azimuth,
                                dec, ha, aoi):
        """
        Test the angle of incidence
        function in ACSE9.SolarModel.SolarArray:

        Example 1.6.1 provided by Duffie and Beckman (2002):

        Inputs
        ------
        latitude = 43.0 degrees; slope = 45 degrees;
        azimuth = 15 degrees; solar declination = -14 degrees;
        hour angle = -22.5 degrees

        Expected output
        ---------------
        Angle of incidence = 35 degrees
        """
        # define dummy SolarArray class object
        time_zone = 0.0
        long = 0.0
        dt = 0.0
        Module_Capacity = 0.0
        Module_Count = 0
        albedo = 0.0
        Derating_Factor = 0.0

        # initialise solar model in a SolarArray class
        dummy = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                      Module_Capacity, Module_Count, albedo,
                                      Derating_Factor)
        # reset relevant attributes to match example
        dummy.Solar_Declination = dec
        dummy.Hour_Angle = ha
        # calculate angle of incidence and store test result
        dummy.Calculate_Angle_of_Incidence()
        test = dummy.Angle_of_Incidence

        assert np.isclose(np.round(test), np.round(aoi))