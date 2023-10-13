import pytest
from app.utils.spectrometer import Spectrometer


@pytest.fixture
def spectrometer():
    return Spectrometer()


def test_connection_failed(spectrometer, mocker):
    mocker.patch('app.utils.spectrometer.Spectrometer.connect',
                 side_effect=Exception)
    with pytest.raises(Exception):
        spectrometer.connect(1)


def test_read_file_failed(spectrometer, mocker):
    mocker.patch('app.utils.spectrometer.pd.read_csv', side_effect=Exception)
    with pytest.raises(Exception):
        spectrometer.read_file("test.csv")


def test_connection_success(spectrometer, mocker):
    mocker.patch('app.utils.spectrometer.Spectrometer.connect',
                 return_value=True)
    assert spectrometer.connect(1) == True
