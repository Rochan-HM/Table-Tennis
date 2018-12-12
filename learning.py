import tensorflow as tf
import cv2  
import mains 
import numpy as np  
import random  
from collections import deque  

no_act = 3

alpha = 0.99

ep_init = 1.0
ep_final = 0.05

no_exp = 5000000000
no_obs = 500000000

no_rep = 500000000

batch_size = 100


def create_grph():
    conv1_wid = tf.Variable(tf.zeros([8, 8, 4, 32]))
    conv1_bre = tf.Variable(tf.zeros([32]))

    conv2_bre = tf.Variable(tf.zeros([4, 4, 32, 64]))
    conv2_wid = tf.Variable(tf.zeros([64]))

    conv3_bre = tf.Variable(tf.zeros([3, 3, 64, 64]))
    conv3_wid = tf.Variable(tf.zeros([64]))

    conv4_bre = tf.Variable(tf.zeros([3136, 784]))
    conv4_wid = tf.Variable(tf.zeros([784]))

    conv5_bre = tf.Variable(tf.zeros([784, no_act]))
    conv5_wid = tf.Variable(tf.zeros([no_act]))

    s = tf.placeholder("float", [None, 84, 84, 4])

    conv1 = tf.nn.relu(tf.nn.conv2d(s, conv1_wid, strides=[1, 4, 4, 1], padding="VALID") + conv1_bre)
    conv2 = tf.nn.relu(tf.nn.conv2d(conv1, conv2_bre, strides=[1, 2, 2, 1], padding="VALID") + conv2_wid)
    conv3 = tf.nn.relu(tf.nn.conv2d(conv2, conv3_bre, strides=[1, 1, 1, 1], padding="VALID") + conv3_wid)
    conv3_flat = tf.reshape(conv3, [-1, 3136])
    conv4 = tf.nn.relu(tf.matmul(conv3_flat, conv4_bre) + conv4_wid)
    conv5 = tf.matmul(conv4, conv5_bre) + conv5_wid

    return s, conv5


def train(inp, out, sess):
    argmax = tf.placeholder("float", [None, no_act])
    placeholder = tf.placeholder("float", [None])

    action = tf.reduce_sum(tf.matmul(out, argmax), reduction_indices=1)
    
    c_func = tf.reduce_mean(tf.square(action - placeholder))
    
    train_step = tf.train.AdamOptimizer(1e-6).minimize(c_func)

    main_game = mains.MainGame()

    dq = deque()

    frame = main_game.curr_frame()
    frame = cv2.cvtColor(cv2.resize(frame, (84, 84)), cv2.COLOR_BGR2GRAY)
    
    ret, frame = cv2.threshold(frame, 1, 255, cv2.THRESH_BINARY)
    
    inp_t = np.stack((frame, frame, frame, frame), axis=2)

    saver = tf.train.Saver()
    sess.run(tf.initialize_all_variables())

    t = 0
    ep = ep_init

    while True:
        out_t = out.eval(feed_dict={inp: [inp_t]})[0]
        
        argmax_t = np.zeros([no_act])

        if random.random() <= ep:
            max_indx = random.randrange(no_act)
        else:
            max_indx = np.argmax(out_t)
        argmax_t[max_indx] = 1

        if ep > ep_final:
            ep -= (ep_init - ep_final) / no_exp

        prize, frame = main_game.next_frame(argmax_t)
        
        frame = cv2.cvtColor(cv2.resize(frame, (84, 84)), cv2.COLOR_BGR2GRAY)
        ret, frame = cv2.threshold(frame, 1, 255, cv2.THRESH_BINARY)
        frame = np.reshape(frame, (84, 84, 1))
        
        inp_t1 = np.append(frame, inp_t[:, :, 0:3], axis=2)

        dq.append((inp_t, argmax_t, prize, inp_t1))

        if len(dq) > no_rep:
            dq.popleft()
        if t > no_obs:
            batch = random.sample(dq, batch_size)

            inp_batch = [d[0] for d in batch]
            argmax_batch = [d[1] for d in batch]
            reward_batch = [d[2] for d in batch]
            inp_t1_batch = [d[3] for d in batch]

            emp_batch = []
            out_batch = out.eval(feed_dict={inp: inp_t1_batch})

            for i in range(0, len(batch)):
                emp_batch.append(reward_batch[i] + alpha * np.max(out_batch[i]))

            train_step.run(feed_dict={placeholder: emp_batch, argmax: argmax_batch, inp: inp_batch})

        inp_t = inp_t1
        t = t + 1

        if t % 10000 == 0:
            saver.save(sess, './' + 'tt' + '-dqn', global_step=t)

        # print("Timesteps:", t, "/ Ep:", ep, "/ Action:", max_indx, "/ Prize", prize,
        #      "/ QMax %e" % np.max(out_t))


def main():
    sess = tf.InteractiveSession()
    inp, out = create_grph()
    train(inp, out, sess)


if __name__ == "__main__":
    main()
