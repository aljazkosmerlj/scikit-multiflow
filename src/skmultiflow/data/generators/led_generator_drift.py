import numpy as np
from skmultiflow.data.generators.led_generator import LEDGenerator



class LEDGeneratorDrift(LEDGenerator):

    """ LEDGeneratorDrift

       Generates instances with 7 numeric attributes  Supports noise
       addition, but in this case the generator will have 24 attribute
       instances.
       The goal is to predict the digit displayed on a seven-segment
       LED display with drift,

       Parameters
       ----------
       seed: int
           random_state for random generation of instances (Default: None)

       noise_percentage: float (Default: 0.0)
           The probability that noise will happen in the generation. At each
           new sample generated, a random probability is generated, and if that
           probability is equal or less than the noise_percentage, the selected data  will
           be switched

       add_noise: bool (Default: False)
           Adds 17 non relevant attributes to the stream.

       n_drift_features : int (Default : False)
           The number of attributes that have drift

        Examples
       --------
       >>> # Imports
       >>> from skmultiflow.data.generators.led_generator_drift import LEDGeneratorDrift
       >>> # Setting up the stream
       >>> stream = LEDGeneratorDrift(seed = 112, noise_percentage = 0.28, add_noise= True, n_drift_features=4)
       >>> stream.prepare_for_use()
       >>> # Retrieving one sample
       >>> stream.next_sample()
       array([[0., 1., 1., 1., 0., 1., 1., 0., 1., 0., 0., 0., 1., 0., 1., 1.,
        1., 0., 0., 0., 0., 0., 1., 1.]])

       >>> # Retrieving 10 samples
       >>> stream.next_sample(10)
        array([[0., 0., 1., 0., 1., 0., 0., 1., 0., 0., 1., 1., 0., 0., 0., 0.,
        1., 1., 0., 0., 0., 0., 1., 1.],
       [0., 1., 1., 0., 0., 0., 1., 1., 1., 0., 1., 0., 0., 0., 1., 1.,
        1., 1., 1., 0., 1., 1., 1., 0.],
       [1., 1., 1., 0., 0., 1., 1., 1., 0., 0., 0., 0., 1., 0., 0., 0.,
        0., 1., 0., 1., 1., 0., 1., 1.],
       [0., 1., 0., 0., 1., 0., 0., 1., 0., 1., 1., 0., 1., 1., 0., 0.,
        1., 1., 0., 1., 1., 1., 1., 0.],
       [0., 1., 1., 0., 1., 0., 1., 0., 1., 1., 0., 1., 1., 0., 1., 0.,
        0., 0., 0., 1., 0., 1., 0., 0.],
       [1., 1., 1., 0., 1., 0., 1., 0., 1., 1., 0., 1., 0., 1., 1., 1.,
        0., 0., 0., 1., 0., 0., 0., 0.],
       [0., 0., 0., 0., 1., 0., 1., 0., 1., 0., 1., 0., 1., 0., 1., 0.,
        1., 1., 1., 0., 1., 0., 0., 1.],
       [1., 0., 0., 0., 1., 1., 0., 1., 1., 1., 0., 0., 0., 0., 0., 1.,
        1., 1., 0., 1., 0., 0., 1., 1.],
       [0., 1., 1., 0., 1., 0., 0., 1., 1., 1., 0., 1., 1., 1., 1., 1.,
        0., 1., 0., 1., 0., 1., 0., 1.],
       [0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.,
        1., 1., 0., 1., 1., 1., 1., 0.]])

       >>> # Generators will have infinite remaining instances, so it returns -1
       >>> stream.n_remaining_samples()
      -1
       >>> stream.has_more_samples()
      True

    """

    _numberAttribute = np.zeros((24,), dtype=int)
    _NUM_IRRELEVANT_ATTRIBUTES = 17

    def __init__(self, seed=None, noise_percentage=0.0, add_noise=False, n_drift_features=0):
        super().__init__(seed=seed, noise_percentage=noise_percentage, add_noise=add_noise)
        self.n_drift_features = n_drift_features

        self.__configure()

    def __configure(self):

        for i in range(self._TOTAL_ATTRIBUTES_INCLUDING_NOISE):
            self._numberAttribute[i] = i

        if self.has_noise() and self.n_drift_features > 0:
            random_int = self.random_state.randint(7)
            offset = self.random_state.randint(self._NUM_IRRELEVANT_ATTRIBUTES)
            for i in range(self.n_drift_features):
                value1 = (i + random_int) % 7
                value2 = 7 + (i + offset) % self._NUM_IRRELEVANT_ATTRIBUTES
                self._numberAttribute[value1] = value2
                self._numberAttribute[value2] = value1

    def next_sample(self, batch_size=1):

        """ next_sample

        An instance is generated based on the parameters passed. If noise
        is included the total number of attributes will be 24, if it's not
        included there will be 7 attributes.



        Parameters
        ----------
        batch_size: int
            The number of samples to return.

        Returns
        -------
        tuple or tuple list
            Return a tuple with the features matrix
            for the batch_size samples that were requested.

        """
        data = np.zeros([batch_size, self.n_cat_features + 1])

        for j in range(batch_size):

            selected = self.random_state.randint(10)

            for i in range(self._NUM_BASE_ATTRIBUTES):
                if (0.01 + self.random_state.rand()) <= self.noise_percentage:
                    data[j, self._numberAttribute[i]] = 1 if (self._ORIGINAL_INSTANCES[selected, i] == 0) else 0
                else:
                    data[j, self._numberAttribute[i]] = self._ORIGINAL_INSTANCES[selected, i]

            if self.has_noise():
                for i in range(self._NUM_BASE_ATTRIBUTES, self._TOTAL_ATTRIBUTES_INCLUDING_NOISE):
                    data[j, self._numberAttribute[i]] = self.random_state.randint(2)

        self.current_sample_x = data[:, :self.n_cat_features]
        return self.current_sample_x

    def get_name(self):
        return "Led Generator with drift - {} target".format(self.n_targets)

    def get_info(self):
        return '  -  n_num_features: ' + str(self.n_num_features) + \
               '  -  n_cat_features: ' + str(self.n_cat_features) + \
               '  -  add_noise: ' + str('True' if self.has_noise() else 'False') + \
               '  -  noise_percentage: ' + str(self.noise_percentage) + \
               '  -  n_drift_features: ' + str(self.n_drift_features) + \
               '  -  random_state: ' + str(self.random_state)