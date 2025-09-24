import numpy as np
import tensorflow as tf
from typing import Any

class GANHealthcareSynthesizer:
    def __init__(self, input_dim: int, latent_dim: int, hidden_dim: int, epochs: int):
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self._build_model()

    def _build_model(self):
        self.generator = tf.keras.Sequential([
            tf.keras.layers.Dense(self.hidden_dim, activation="relu", input_shape=(self.latent_dim,)),
            tf.keras.layers.Dense(self.input_dim, activation="sigmoid")
        ])
        self.discriminator = tf.keras.Sequential([
            tf.keras.layers.Dense(self.hidden_dim, activation="relu", input_shape=(self.input_dim,)),
            tf.keras.layers.Dense(1, activation="sigmoid")
        ])
        self.discriminator.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        self.discriminator.trainable = False
        noise = tf.keras.layers.Input(shape=(self.latent_dim,))
        generated_data = self.generator(noise)
        validity = self.discriminator(generated_data)
        self.combined = tf.keras.Model(noise, validity)
        self.combined.compile(optimizer="adam", loss="binary_crossentropy")
        self.discriminator.trainable = True

    def train(self, real_data: Any):
        real_data = real_data.values if hasattr(real_data, "values") else real_data
        batch_size = 64
        for epoch in range(self.epochs):
            idx = np.random.randint(0, real_data.shape[0], batch_size)
            real_batch = real_data[idx]
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            gen_samples = self.generator.predict(noise)
            d_loss_real = self.discriminator.train_on_batch(real_batch, np.ones((batch_size, 1)))
            d_loss_fake = self.discriminator.train_on_batch(gen_samples, np.zeros((batch_size, 1)))
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            g_loss = self.combined.train_on_batch(noise, np.ones((batch_size, 1)))

    def generate(self, n_samples: int) -> np.ndarray:
        noise = np.random.normal(0, 1, (n_samples, self.latent_dim))
        synthetic_data = self.generator.predict(noise)
        return synthetic_data