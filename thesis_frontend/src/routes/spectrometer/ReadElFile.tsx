import { useCallback, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import LoadingSpinner from '../../components/main/LoadingSpinner';
import { useToast, EToastTypes } from '../../components/Context/ToastContext';
import FileDropzone from '../../components/main/FileDropzone';
import 'chartjs-plugin-zoom';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import CustomLineChart from '../../components/main/CustomLineChart';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import TabPanel, { a11yProps } from '../../components/main/TabPanel';

type TElData = {
  metadata: Record<string, string>;
  wavelengths: number[];
  spectralPower: number[];
  energy: number[];
  photonFlux: number[];
};

const ReadElFile = () => {
  const { showTypedToast } = useToast();
  const [tab, setTab] = useState(0);

  const readFile = useMutation({
    mutationKey: ['readFile'],
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(
        '/backend/spectrometer/read_el_file',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data as TElData;
    },
    onError: (error: any) => {
      showTypedToast(EToastTypes.ERROR, error?.message);
    },
    onSuccess: (data) => {
      showTypedToast(EToastTypes.SUCCESS, 'Successfully read file');
      setTab(1);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Handle the dropped files here
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      readFile.mutate(file);
    } else {
      showTypedToast(EToastTypes.ERROR, 'No file was dropped.');
    }
  }, []);

  // Rendering the loading spinner if the file is being read
  if (readFile.isLoading) return <LoadingSpinner />;
  // Rendering the error message if the file could not be read
  if (readFile.isError) return <div>Error: {readFile.error}</div>;

  return (
    <>
      <Tabs
        value={tab}
        onChange={(e, v) => setTab(v)}
        sx={{
          paddingBottom: 2,
        }}
      >
        <Tab label="File Upload" value={0} {...a11yProps(0)} />
        <Tab label="Wavelength v Spectral Power" value={1} {...a11yProps(1)} />
        <Tab label="Energy v Photon Flux" value={2} {...a11yProps(2)} />
      </Tabs>

      <TabPanel value={tab} index={0}>
        <Card>
          <CardHeader
            title="Read EL File"
            subheader="Upload a .csv file containing EL data."
          />
          <CardContent
            sx={{
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <FileDropzone
              onDrop={onDrop}
              onDropRejected={() => {
                showTypedToast(EToastTypes.ERROR, 'File type not supported');
              }}
            />
          </CardContent>
        </Card>
      </TabPanel>
      <TabPanel value={tab} index={1}>
        <CustomLineChart
          xAxis={readFile?.data?.wavelengths}
          yAxis={readFile?.data?.spectralPower}
          title="Wavelength vs Spectral Power"
          metadata={readFile?.data?.metadata}
          xLabel="Wavelength (nm)"
          yLabel="Spectral Power (μW/nm)"
          seriesLabel="EL Data"
        />
      </TabPanel>
      <TabPanel value={tab} index={2}>
        <CustomLineChart
          xAxis={readFile?.data?.energy}
          yAxis={readFile?.data?.photonFlux}
          title="Energy vs Photon Flux"
          metadata={readFile?.data?.metadata}
          xLabel="Energy (eV)"
          yLabel="Photon Flux (photon/s/nm)"
          seriesLabel="EL Data"
        />
      </TabPanel>
    </>
  );
};

export default ReadElFile;
