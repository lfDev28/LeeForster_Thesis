import {
  TCalibrationById,
  TCalibrationBySerial,
} from '../../routes/spectrometer/Calibration';
import { TLineChart } from '../main/CustomLineChart';

import React from 'react';
import CustomLineChart from '../main/CustomLineChart';

type TCalibrationChartProps = {
  step: number;
  data: TCalibrationById;
};

const CalibrationChart: React.FC<TCalibrationChartProps> = ({ step, data }) => {
  const chartPropsArray = getChartPropsForStep(step, data);

  return (
    <>
      {chartPropsArray.map((chartProps, index) => {
        <CustomLineChart key={index} {...chartProps} />;
      })}
    </>
  );
};

export default CalibrationChart;

function getChartPropsForStep(
  step: number,
  data: TCalibrationById | undefined
): TLineChart[] | [] {
  if (!data) {
    return [];
  }

  const allSerialData = Object.values(data.calibration_by_serial);

  const wavelengths = allSerialData.flatMap(
    (serialData) => serialData.wavelengths
  );

  switch (step) {
    case 0:
      // Stitch together the data
      const darkSpectrum = allSerialData.flatMap(
        (serialData) => serialData.dark_spectrum
      );
      const darkAuxSpectrum = allSerialData.flatMap(
        (serialData) => serialData.dark_aux_spectrum
      );

      return [
        {
          xAxis: wavelengths,
          yAxis: darkSpectrum,
          title: 'Dark Spectrum',
          xLabel: 'Wavelength (nm)',
          yLabel: 'Dark Spectrum (counts)',
          metadata: undefined,
          seriesLabel: 'Dark Spectrum',
        },
        {
          xAxis: wavelengths,
          yAxis: darkAuxSpectrum,
          title: 'Dark Aux Spectrum',
          xLabel: 'Wavelength (nm)',
          yLabel: 'Dark Aux Spectrum (counts)',
          metadata: undefined,
          seriesLabel: 'Dark Aux Spectrum',
        },
      ];
    case 1:
      const calibrationSpectrum = allSerialData.flatMap(
        (serialData) => serialData.calibration_spectrum
      );
      return [
        {
          xAxis: wavelengths,
          yAxis: calibrationSpectrum,
          title: 'Calibration Spectrum',
          xLabel: 'Wavelength (nm)',
          yLabel: 'Calibration Spectrum (counts)',
          metadata: undefined,
          seriesLabel: 'Calibration Spectrum',
        },
      ];
    case 2:
      const auxCalibrationSpectrum = allSerialData.flatMap(
        (serialData) => serialData.aux_calibration_spectrum
      );
      return [
        {
          xAxis: wavelengths,
          yAxis: auxCalibrationSpectrum,
          title: 'Aux Calibration Spectrum',
          xLabel: 'Wavelength (nm)',
          yLabel: 'Aux Calibration Spectrum (counts)',
          metadata: undefined,
          seriesLabel: 'Aux Calibration Spectrum',
        },
      ];
    case 3:
      const auxDutSpectrum = allSerialData.flatMap(
        (serialData) => serialData.aux_dut_spectrum
      );
      return [
        {
          xAxis: wavelengths,
          yAxis: auxDutSpectrum,
          title: 'Aux DUT Spectrum',
          xLabel: 'Wavelength (nm)',
          yLabel: 'Aux DUT Spectrum (counts)',
          metadata: undefined,
          seriesLabel: 'Aux DUT Spectrum',
        },
      ];
    default:
      return [];
  }
}
