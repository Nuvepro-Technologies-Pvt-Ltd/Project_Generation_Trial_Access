import numpy as np
import tensorflow as tf
from typing import Any

class Sampling(tf.keras.layers.Layer):
    def call(self, inputs, **kwargs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

class VAEHealthcareSynthesizer:
    def __init__(self, input_dim: int, latent_dim: int, hidden_dim: int, epochs: int):
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self._build_model()

    def _build_model(self):
        encoder_inputs = tf.keras.layers.Input(shape=(self.input_dim,))
        x = tf.keras.layers.Dense(self.hidden_dim, activation="relu")(encoder_inputs)
        z_mean = tf.keras.layers.Dense(self.latent_dim, name="z_mean")(x)
        z_log_var = tf.keras.layers.Dense(self.latent_dim, name="z_log_var")(x)
        z = Sampling()([z_mean, z_log_var])
        self.encoder = tf.keras.Model(encoder_inputs, [z_mean, z_log_var, z], name="encoder")
        latent_inputs = tf.keras.layers.Input(shape=(self.latent_dim,))
        x = tf.keras.layers.Dense(self.hidden_dim, activation="relu")(latent_inputs)
        decoder_outputs = tf.keras.layers.Dense(self.input_dim, activation="sigmoid")(x)
        self.decoder = tf.keras.Model(latent_inputs, decoder_outputs, name="decoder")
        outputs = self.decoder(self.encoder(encoder_inputs)[2])
        self.model = tf.keras.Model(encoder_inputs, outputs, name="vae")
        reconstruction_loss = tf.keras.losses.binary_crossentropy(encoder_inputs, outputs)
        reconstruction_loss = tf.reduce_mean(reconstruction_loss) * self.input_dim
        kl_loss = -0.5 * tf.reduce_mean(
            1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
        )
        vae_loss = reconstruction_loss + kl_loss
        self.model.add_loss(vae_loss)
        self.model.compile(optimizer="adam")

    def train(self, real_data: Any):
        real_data = real_data.values if hasattr(real_data, "values") else real_data
        self.model.fit(real_data, real_data, epochs=self.epochs, batch_size=64, verbose=0)

    def generate(self, n_samples: int) -> np.ndarray:
        z = np.random.normal(size=(n_samples, self.latent_dim))
        synthetic = self.decoder.predict(z)
        return synthetic