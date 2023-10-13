import pytest
from app.utils.smu import Smu


@pytest.fixture
def smu():
    return Smu()

#  As all of the values are dynamic, I am currently just testing that they are erroring correctly.


def test_connect_failed(smu, mocker):
    mocker.patch('app.utils.smu.Keithley2450', side_effect=Exception)
    with pytest.raises(Exception):
        smu.connect(1)


def test_iv_sweep_failed(smu, mocker):
    mocker.patch('app.utils.smu.Smu.setup_voltage_source',
                 side_effect=Exception)
    with pytest.raises(Exception):
        smu.IV_Sweep(1, {})


def test_read_file_failed(smu, mocker):
    mocker.patch('app.utils.smu.pd.read_csv', side_effect=Exception)
    with pytest.raises(Exception):
        smu.read_file("test.csv")


def test_setup_voltage_source_failed(smu, mocker):
    mocker.patch('app.utils.smu.Smu.connect', side_effect=Exception)
    with pytest.raises(Exception):
        smu.setup_voltage_source(1, 1)
