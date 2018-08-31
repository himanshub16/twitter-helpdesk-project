<template>

<v-layout
  column
  class="chat-container"
  >

  <v-flex
    v-if="tweets"
    v-for="msg in tweets"
    class="messages"
    >
    <Message :msg="msg" />
  </v-flex>

  <v-layout row>
    <v-flex md5></v-flex>
    <v-flex md7>
      <v-card flat class="tweet-card" color="yellow lighten-4">
        <div class="tweet-userinfo">
          <v-icon small>person</v-icon>
          <span class="body-2">{{ screenName }}</span>
        </div>
        <v-card-text class="input-box">
          <v-textarea
            box textarea
            auto-grow
            label="Type your reply here..."
            ></v-textarea>
            <v-btn outline>Send</v-btn>
        </v-card-text>
      </v-card>
    </v-flex>
  </v-layout>
</v-layout>

</template>

<script>
import Message from './chat/Message.vue';

export default {
  props: ['tweets'],

  components: {
    Message,
  },
  data() {
    return {
      msgPos: true,
    };
  },
  computed: {
    screenName() {
      return this.$route.params.screenName;
    },
  },
  methods: {
    msgPosition(msg) {
      return msg.sender == this.$route.params.screenName;
    },
  },
  created() {
    if (!this.tweets) return;
    console.log(this.tweets, this.tweets.length);
  },
};
</script>


<style scoped>
.msg-right {
    background-color: blue;
}
.tweet-card {
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-top: 10px;
}
.tweet-userinfo {
    padding: 2px 8px 0px;
}
.input-box {
    padding: 5px;
}
.chat-container {
    margin: 0px !important;
    margin-right: 5px;
    padding-left: 5px;
    border: none !important;
    max-height: 100%;
}
.input-box .v-textarea {
    padding: 0 5px;
    margin-bottom: -25px;
}
.messages {
    margin-top: 2em;
}
</style>
