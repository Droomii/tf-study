# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 14:27:42 2020

@author: DATALAB_3
"""

import tensorflow.compat.v1 as tf
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets('MNIST_data/', one_hot=True)

# Using Interactive session makes it the default sessions so we do not need to pass sess
sess = tf.InteractiveSession()

# Define placeholders for MNIST input data
x = tf.placeholder(tf.float32, shape=[None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])

# change the MNIST input data from a list of values to a 28 x 28 x 1 grascale value cube
# which the Convolution NN can use
#                       -1 : make this a list of the other dimensions
x_image = tf.reshape(x, [-1,28,28,1], name="x_image")

# Define helper functions to created weights and biases variables, and convolution, and pooling layers
# Relu is used as activation function.  Must be initialized to a small positive number
#  and with some noise so it doesn't end up going to zero when comparing diffs
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

# Convolution and Pooling - we do Convolution, and then pooling to control overfitting
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')


# Define layers in the NN
    
# ------------ 1st convolution layer ------------------
# 32 features for each 5x5 patch of the image
W_conv1 = weight_variable([5,5,1,32]) # width, height, channel(grayscale, so 1), num. of features
b_conv1 = bias_variable([32])

# Do convolution on images, add bias and push through ReLU activation
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

# take results and run through max_pool
h_pool1 = max_pool_2x2(h_conv1)


# ------------- 2nd convolution layer --------------
# process the 32 features from conv. layer 1, in 5x5 patch. Return 64 features weights and biases
W_conv2 = weight_variable([5,5,32,64]) # width, height, channel(32 features), num. of features
b_conv2 = bias_variable([64])

# Do convolution on images, add bias and push through ReLU activation
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

# take results and run through max_pool
h_pool2 = max_pool_2x2(h_conv2)

# ------------- Fully Connected Layer ---------------
W_fc1 = weight_variable([7*7*64, 1024])
b_fc1 = bias_variable([1024])


# Connect output of pooling layer 2 as input to full connected layer
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

# dropout some neurons to reduce overfitting
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# Readout layer
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

# Define model
y_conv = tf.matmul(h_fc1_drop, W_fc2)  + b_fc2

# Loss measurement
cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))


# Loss optimization
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

# correct prediction
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_,1))

# get accuracy
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess.run(tf.global_variables_initializer())

# ------------------------train model-------------------------
import time

# define number of steps and how often we display progress
num_steps = 3000
display_every = 100

# Start timer
start_time = time.time()
end_time = time.time()

for i in range(num_steps):
    batch = mnist.train.next_batch(50)
    train_step.run(feed_dict={x:batch[0], y_:batch[1], keep_prob:0.5})
    
    # Periodic status display
    if i % display_every == 0:
        train_accuracy = accuracy.eval(feed_dict={
                x: batch[0],
                y_ : batch[1],
                keep_prob : 1.0})
        end_time = time.time()
        print("step {0}, elapsed time {1:.2f} sec, training accuracy {2:.3f}%".format(i, end_time-start_time, train_accuracy*100))
        
# display summary
# Time to train
end_time = time.time()
print("total training time for {0} batches : {1:.2f} sec.".format(i+1, end_time-start_time))

# Accuracy on test data
print("Test accuracy {0:.3f}%".format(accuracy.eval(feed_dict={
        x : mnist.test.images,
        y_ : mnist.test.labels,
        keep_prob : 1.0}) *100.0))
    
sess.close()