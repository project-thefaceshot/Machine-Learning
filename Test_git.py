import numpy as np
import tensorflow as tf

ckptName = "/model.ckpt"
input_data = 'TestData.csv'
data_xy = np.loadtxt(input_data, delimiter=',', dtype=np.float32)
data_N = len(data_xy)

X = tf.placeholder(tf.float32, [None, 96 * 96 * 1])
Y = tf.placeholder(tf.int32, [None, 1])
Y_one_hot = tf.one_hot(Y, 7)
Y_one_hot = tf.reshape(Y_one_hot, [-1, 7])
X_img = tf.reshape(X, [-1, 96, 96, 1])

W1 = tf.Variable(tf.random_normal([3, 3, 1, 64], stddev=0.01))
L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.relu(L1)
L1 = tf.nn.local_response_normalization(L1, depth_radius=2, alpha=2e-05, beta=0.75, bias=1.0)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

W2 = tf.Variable(tf.random_normal([3, 3, 64, 128], stddev=0.01))
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.relu(L2)
L2 = tf.nn.local_response_normalization(L2, depth_radius=2, alpha=2e-05, beta=0.75, bias=1.0)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

W3 = tf.Variable(tf.random_normal([3, 3, 128, 256], stddev=0.01))
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')
L3 = tf.nn.relu(L3)
L3 = tf.nn.max_pool(L3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

W4 = tf.Variable(tf.random_normal([3, 3, 256, 512], stddev=0.01))
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')
L4 = tf.nn.relu(L4)
L4 = tf.nn.max_pool(L4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

W5 = tf.Variable(tf.random_normal([6, 6, 512, 512], stddev=0.01))
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')
L5 = tf.nn.relu(L5)
L5 = tf.nn.max_pool(L5, ksize=[1, 6, 6, 1], strides=[1, 6, 6, 1], padding='SAME')
L5_flat = tf.reshape(L5, [-1, 1 * 1 * 512])

W6 = tf.get_variable("W6", shape=[512 * 1 * 1, 4096], initializer=tf.contrib.layers.xavier_initializer())
b6 = tf.Variable(tf.random_normal([4096]))
L6 = tf.nn.relu(tf.matmul(L5_flat, W6) + b6)

W7 = tf.get_variable("W7", shape=[4096, 1000], initializer=tf.contrib.layers.xavier_initializer())
b7 = tf.Variable(tf.random_normal([1000]))
L7 = tf.nn.relu(tf.matmul(L6, W7) + b7)

W8 = tf.get_variable("W8", shape=[1000, 7], initializer=tf.contrib.layers.xavier_initializer())
b8 = tf.Variable(tf.random_normal([7]))
logits = tf.matmul(L7, W8) + b8

prediction = tf.argmax(logits, 1)
correct_prediction = tf.equal(prediction, tf.argmax(Y_one_hot, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
sess = tf.Session()
sess.run(tf.global_variables_initializer())

trueCnt = 0
test_count = 0
i = 0
while i <= data_N:
    batch_test_x = data_xy[i:(i+300), 0:-1]
    batch_test_y = data_xy[i:(i+300), [-1]]
    predict_output = sess.run(prediction, feed_dict={X: batch_test_x})
    for p, y in zip(predict_output, batch_test_y.flatten()):
        if p == int(y):
            trueCnt = trueCnt + 1
        test_count = test_count + 1
    i += 300
print('Accuracy:', float(trueCnt / test_count))
sess.close()