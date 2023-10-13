import React from 'react';
import Card from '@mui/material/Card';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import IconButton from '@mui/material/IconButton';
import Delete from '@mui/icons-material/Delete';
import Tooltip from '@mui/material/Tooltip';
import Edit from '@mui/icons-material/Edit';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { useModal } from '../../components/Context/ModalContext';
import { useToast, EToastTypes } from '../../components/Context/ToastContext';
import Visibility from '@mui/icons-material/Visibility';
import { Link } from 'react-router-dom';
import { Typography } from '@mui/material';

const IvList = () => {
  const { showTypedToast } = useToast();
  const { deleteModal } = useModal();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['ivs'],
    queryFn: async () => {
      const res = await axios.get('/backend/smu/iv', {
        headers: {
          'Content-Type': 'application/json',
        },
      });

    
      return res.data;
    
        },
  });

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      maxWidth: 300,
      flex: 1,
    },
    {
      field: 'start_time',
      headerName: 'Start Time',
      type: 'date',
      flex: 1,
      valueFormatter: (params) => {
        return new Date(params?.value?.$date).toLocaleString('en-AU') || '';
      },
    },
    {
      field: 'end_time',
      type: 'date',
      headerName: 'End Time',
      flex: 1,
      valueFormatter: (params) => {
        return new Date(params?.value?.$date).toLocaleString('en-AU') || '';
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      flex: 1,
    },
    {
      field: 'action',
      headerName: 'Action',
      maxWidth: 200,
      minWidth: 200,
      flex: 1,
      renderCell: (params) => {
        return (
          <div className="space-x-2">
            <Tooltip title="Show Data">
              <Link to={{
                pathname: `/experiment/iv/${params.row._id.$oid}`
              }}>
              <IconButton aria-label="view" size="small" color="primary" >
                <Visibility fontSize="inherit" />
              </IconButton>
              </Link>
            </Tooltip>
            <Tooltip title="Delete Experiment">
              <IconButton
                aria-label="delete"
                size="small"
                color="error"
                onClick={() => deleteModal(handleDelete, params.row._id.$oid, `Are you sure you want to delete item "${params.row.name || params.row._id.$oid}"?`)}
              >
                <Delete fontSize="inherit" />
              </IconButton>
            </Tooltip>
          </div>
        );
      },
    },
  ];

  const deleteIv = useMutation({
    mutationKey: ['delete_iv'],
    mutationFn: async (id: string) => {
      const res = await axios.delete(`/backend/smu/iv/${id}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return res.data;
    },
    onError: (err) => {
      showTypedToast(EToastTypes.ERROR, JSON.stringify(err));
    },
    onSuccess: () => {
      showTypedToast(EToastTypes.SUCCESS, 'Successfully deleted IV Experiment');
      refetch();
    },
  });

  const handleDelete = (id: string) => {
    deleteIv.mutate(id);
  };

  return (
    <>
    <Typography variant="h4" sx={{marginBottom: 2}}>IV Experiments</Typography>
    <Card>
      
      <DataGrid
        columns={columns}
        rows={data || []}
        loading={isLoading}
        sx={{
          height: 500,
          width: '100%',
        }}
        getRowId={(row) => row._id.$oid}
      />
    </Card>
    </>
  );
};

export default IvList;
