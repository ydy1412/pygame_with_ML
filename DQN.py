import tensorflow as tf
import numpy as np
import random

# DQN class
# DQN has session variable.
# To create DQN model, excute "dqn = DQN(session, input_shape, output_shape)"
# To predict output, excute "dqn.predict(input_data)"
# To update DQN model, excute "dqn.update(input_data,y_data)
class DQN :
    def __init__(self,session,input_size,output_size,name = "main"):
        self.session = session
        self.input_size = input_size
        self.output_size = output_size
        self.net_name = name

        self.build_network()

    def  build_network(self,h_size = 30,l_rate = 0.1):
        with tf.variable_scope("input", reuse=tf.AUTO_REUSE):
            self._X = tf.placeholder(tf.float32,[None,40,30,1])
            self._X_reshape = tf.reshape(self._X,shape = [-1,40,30,1])
            self._Y = tf.placeholder(shape=[None, self.output_size], dtype=tf.float32)
        # with tf.variable_scope("con1", reuse=tf.AUTO_REUSE):
        #     self.conv1 = tf.layers.conv2d(self._X_reshape ,filters = 64,kernel_size = 3,strides = 1,
        #                              padding = 'SAME',activation = tf.nn.relu)
        # with tf.variable_scope("pool1", reuse=tf.AUTO_REUSE):
        #     self.pool1 = tf.nn.max_pool(self.conv1,ksize = [1,2,2,1],strides = [1,2,2,1],padding = 'VALID')
        # with tf.variable_scope("conv2", reuse=tf.AUTO_REUSE):
        #     self.conv2 = tf.layers.conv2d(self.pool1,filters = 32,kernel_size = 3,strides =  1,
        #                                   padding = 'SAME',activation = tf.nn.relu)
        with tf.variable_scope("poo2", reuse=tf.AUTO_REUSE):
            # self.pool2 = tf.nn.max_pool(self.conv1,ksize = [1,2,2,1],strides = [1,2,2,1],padding = 'VALID')
            self.pool_flat = tf.layers.flatten(self._X)

        with tf.variable_scope("fc", reuse=tf.AUTO_REUSE):
            self.fc1 = tf.layers.dense(self.pool_flat,256,activation = tf.nn.relu)
            self.fc2 = tf.layers.dense(self.fc1, 40, activation=tf.nn.relu)

        with tf.variable_scope("output", reuse=tf.AUTO_REUSE):
            self.logits = tf.layers.dense(self.fc2,self.output_size)

        with tf.variable_scope("train", reuse=tf.AUTO_REUSE):
            self._loss = tf.reduce_mean(tf.square(self._Y-self.logits))
            self.optimizer = tf.train.AdamOptimizer(learning_rate=l_rate)
            self._training_op = self.optimizer.minimize(self._loss)

    def predict(self,state):
        x = np.reshape(state,[-1,40,30,1])
        return self.session.run(self.logits,feed_dict= {self._X : x})

    def update(self , x_stack, y_stack):
        x_stack = np.reshape(x_stack, [-1, 40, 30, 1])
        return self.session.run([self._loss,self._training_op],feed_dict ={self._X:x_stack,self._Y :y_stack})

# For batch train.
def replay_train(mainDQN,targetDQN,train_batch,dis):
    # 0 크기의 numpy array를 만듬
    x_stack = np.empty(0).reshape(0,mainDQN.input_size)
    y_stack = np.empty(0).reshape(0,mainDQN.output_size)
    for state, action, reward, next_state, done in train_batch:
        Q = mainDQN.predict(state)
        if done :
            Q[0,action] = reward
        else :
            Q[0,action] = reward + dis * np.max(targetDQN.predict(next_state))
        y_stack = np.vstack([y_stack,Q])
        # state shape = (0,input_size)
        x_stack = np.vstack([x_stack,state])
    return mainDQN.update(x_stack,y_stack)

# Copy variables of model and put into list.
def get_copy_var_ops(*,dest_scope_name = "target",src_scope_name = "main") :
    op_holder = []
    # get_collection에 scope 이름을 주면 모든 변수들을 가져옴
    src_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_RESOURCE_VARIABLES,scope = src_scope_name)
    dest_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_RESOURCE_VARIABLES,scope = dest_scope_name )
    for src_var,dest_var in zip(src_vars,dest_vars) :
        op_holder.append(dest_var.assign(src_var.value()))
    return op_holder