import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { TCalibrationFormProps } from './CalibrationStepper';

const AuxDutForm = ({ mutation, lampMutation, cal_id, has_data }: TCalibrationFormProps) => {
  return (
    <Box sx={{ mt: 2, padding: 3, border: '1px solid #ddd', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Aux + DUT
      </Typography>
      <Typography paragraph>
        Leave the auxiliary lamp on, and remove the calibration lamp. Then mount
        the DUT.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => mutation?.mutate(cal_id)}
        disabled={
          mutation?.isLoading || mutation?.isSuccess || !lampMutation?.isSuccess || has_data
        }
      >
        Measure AUX + DUT
      </Button>
    </Box>
  );
};

export default AuxDutForm;
