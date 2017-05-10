import numpy as np
import pyuvdata.parameter as uvp
import copy
import pickle
import uuid

class CalFlagWeights():
    """
    Defines a class for storing weights and flags in calibration
    Properties: 
    """
      """ A class defining a calibration """
    def __init__(self,id):
        self.id=id #unique identifier. 
        radian_tol = 10 * 2 * np.pi * 1e-3 / (60.0 * 60.0 * 360.0)
        self._Nfreqs = uvp.UVParameter('Nfreqs',
                                       description='Number of frequency channels',
                                       expected_type=int)
        self._Njones = uvp.UVParameter('Njones',
                                       description='Number of polarizations calibration'
                                       'parameters (Number of jones matrix elements.).',
                                       expected_type=int)
        self._Ntimes = uvp.UVParameter('Ntimes',
                                       description='Number of times',
                                       expected_type=int)
        self._history = uvp.UVParameter('history',
                                        description='String of history, units English',
                                        form='str', expected_type=str)
        self._Nspws = uvp.UVParameter('Nspws', description='Number of spectral windows '
                                      '(ie non-contiguous spectral chunks). '
                                      'More than one spectral window is not '
                                      'currently supported.', expected_type=int)

        desc = ('Frequency range that gain solutions are valid for.',
                'list: (start_frequency, end_frequency) in Hz.')
        self._freq_range = uvp.UVParameter('freq_range',
                                           description=desc,
                                           form=(2,),
                                           expected_type=float)

        desc = ('Time range (in JD) that gain solutions are valid for.',
                'list: (start_time, end_time) in JD.')
        self._time_range = uvp.UVParameter('time_range',
                                           description=desc,
                                           form=(2,),
                                           expected_type=float)

        desc = ('Name of telescope. e.g. HERA. String.')
        self._telescope_name = uvp.UVParameter('telescope_name',
                                               description=desc,
                                               form='str',
                                               expected_type=str)

        desc = ('Number of antennas with data present (i.e. number of unique '
                'entries in ant_array). May be smaller ' +
                'than the number of antennas in the telescope')
        self._Nants_data = uvp.UVParameter('Nants_data', description=desc,
                                           expected_type=int)

        desc = ('Number of antennas in the array. May be larger ' +
                'than the number of antennas with data')
        self._Nants_telescope = uvp.UVParameter('Nants_telescope',
                                                description=desc,
                                                expected_type=int)

        desc = ('Array of antenna indices for data arrays, shape (Nants_data), '
                'type = int, 0 indexed')
        self._ant_array = uvp.UVParameter('ant_array', description=desc,
                                          expected_type=int, form=('Nants_data',))

        desc = ('List of antenna names, shape (Nants_telescope), '
                'with numbers given by antenna_numbers (which can be matched '
                'to ant_array). There must be one entry here for each unique '
                'entry in ant_array, but there may be extras as well.')
        self._antenna_names = uvp.UVParameter('antenna_names',
                                              description=desc,
                                              form=('Nants_telescope',),
                                              expected_type=str)

        desc = ('List of integer antenna numbers corresponding to antenna_names,'
                'shape (Nants_telescope). There must be one entry here for each unique '
                'entry in ant_array, but there may be extras as well.')
        self._antenna_numbers = uvp.UVParameter('antenna_numbers',
                                                description=desc,
                                                form=('Nants_telescope',),
                                                expected_type=int)

        desc = 'Array of frequencies, shape (Nspws, Nfreqs), units Hz'
        self._freq_array = uvp.UVParameter('freq_array', description=desc,
                                           form=('Nspws', 'Nfreqs'),
                                           expected_type=np.float,
                                           tols=1e-3)  # mHz

        desc = ('Channel width of of a frequency bin. Units Hz.')
        self._channel_width = uvp.UVParameter('channel_width',
                                              description=desc,
                                              expected_type=np.float,
                                              tols=1e-3)

        desc = ('Array of antenna polarization integers, shape (Njones). '
                'linear pols -5:-8 (jxx, jyy, jxy, jyx).'
                'circular pols -1:-4 (jrr, jll. jrl, jlr).')

        self._jones_array = uvp.UVParameter('jones_array',
                                            description=desc,
                                            expected_type=int,
                                            acceptable_vals=list(np.arange(-8, 0)),
                                            form=('Njones',))

        desc = ('Array of times, center of integration, shape (Ntimes), ' +
                'units Julian Date')
        self._time_array = uvp.UVParameter('time_array', description=desc,
                                           form=('Ntimes',),
                                           expected_type=np.float,
                                           tols=1e-3 / (60.0 * 60.0 * 24.0))

        desc = ('Integration time of a time bin (s).')
        self._integration_time = uvp.UVParameter('integration_time',
                                                 description=desc,
                                                 expected_type=np.float,
                                                 tols=1e-3)  # 1ms

        desc = ('Orientation of the physical dipole corresponding to what is '
                'labelled as the x polarization. Values are east '
                '(east/west orientation),  north (north/south orientation) or '
                'unknown.')
        self._x_orientation = uvp.UVParameter('x_orientation', description=desc,
                                              expected_type=str,
                                              acceptable_vals=['east', 'north', 'unknown'])

        desc=('Array of flags applied to data only in calibration. Evaluated with or to any'
              'other pre-existing flags on the data set'
              'shape: (Nblts,Nspws,Nfreqs,Npols)')
        
        self._flag_array=uvp.UVParameter('flag_array',description=desc,
                                         form=('Nblts','Nspws','Nfreqs','Npols'),
                                         expected_type=np.bool)
        desc=('Array of weights applied to data only in calibration.'
              'shape: (Nblts,Nspws,Nfreqs,Npols)')
        self._weights_array=uvp.UVParameter('weights_array',description=desc,
                                           form=('Nblts','Nspws','Nfreqs','Npols'),
                                           expected_type=np.float)
        
        self._chi_squares=uvp.UVParameter('chi_squares',description=desc,
                                          form=('Nants_data','NFreqs','NPols'),
                                          expected_type=float,required=False)
    
   
        # String to add to history of any files written with this version of pyuvdata
        self.pyuvdata_version_str = ('  Read/written with pyuvdata version: ' +
                                     uvversion.version + '.')
        if uvversion.git_hash is not '':
            self.pyuvdata_version_str += ('  Git origin: ' + uvversion.git_origin +
                                          '.  Git hash: ' + uvversion.git_hash +
                                          '.  Git branch: ' + uvversion.git_branch +
                                          '.  Git description: ' + uvversion.git_description)

        self._noise_tavg=uvp.UVParameter('noise_tavg',
                                         description='noise levels in uncalibrated'
                                         'visibilities computed by taking differences'
                                         'in frequency and restricted average over'
                                         ' all times',
                                         form=('Nbls','NFreqs','Npols'),
                                         expected_type=np.float,required=False)
        self._noise_favg=uvp.UVParameter('noise_favg',
                                         description='noise levels in uncalibrated'
                                         'visibilities computed by taking differences'
                                         'in time and restricted average over'
                                         ' all frequency',
                                         form=('Nblts','Npols'),
                                         expected_type=np.float,required=False)
      
            
        def from_file(self,datafile,mode='UVDATA'):
            '''
            initialize flagweights object from calFlagWeights file
            args: name of data file to read in
            '''
            assert mode in ['UVDATA','CALFLAGWEIGHTS']:
            if mode=='CALFLAGWEIGHTS':
                data=pickle.load(open(datafile,"rb"))
            self.Nfreqs=copy.copy(data.Nfreqs)
            self.Njones=copy.copy(data.Njones)
            self.Ntimes=copy.copy(data.Ntimes)
            self.Nspws=copy.copy(uvdata.Nspws)
            self.Nbls=copy.copy(uvdata.Nbls)
            self.Nblts=copy.copy(uvdata.Nblts)
            self.uvw=copy.copy(uvdata.uvw)
            self.history=copy.copy(data.history)
            self.Nspws=copy.copy(data.Nspws)
            self.freq_range=copy.copy(data.freq_range)
            self.time_rage=copy.copy(data.time_range)
            self.telescope_name=copy.copy(data.telescope_name)
            self.Nants_data=copy.copy(data.Nants_data)
            self.Nants_telescope=copy.copy(data.Nants_telescope)
            self.ant_array=copy.copy(data.ant_array)
            self.antenna_names=copy.copy(data.antenna_names)
            self.antenna_numbers=copy.copy(data.antenna_numbers)
            self.freq_array=copy.copy(data.freq_array)
            self.channel_width=copy.copy(data.channel_width)
	    self.jones_array=copy.copy(data.jones_array)
	    self.time_array=copy.copy(data.time_array)
            self.integration_time=copy.copy(data.integration_time)
            self.x_orientation=copy.copy(data.x_orientation)
            self.flag_array=copy.copy(data.flag_array)
            self.weights_array=copy.copy(data.weights_array)
            del(data)


        def read_data
        def to_file(self,datafile,clobber=False):
            '''
            write calweights object to a file using pickle
            '''
            if clobber or not(os.path.exists(datafile)):
                pickle.dump(self,open(datafile,"wb"))
            else:
                print("%s already exists. Use clobber=True to overwrite"%datafile)
            

            
