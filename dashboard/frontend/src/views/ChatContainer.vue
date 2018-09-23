<template>
<v-content
  fixed
  class="content-padding"
  >
  <v-container fluid grid-list-md fill-height
               class="container-padding"
               >
    <v-layout row fill-height class="no-border">

      <v-flex d-flex xs12 sm6 md8 elevation-0>

        <div class="chat-container">
          <div class="chat-controls">
            <v-progress-circular
              indeterminate
              color="primary"
              v-if="changingStatus"
              >
            </v-progress-circular>

            <v-btn
              color="blue darken-1"
              outline
              v-if="conversation.status!='open'"
              v-on:click="changeStatus('open')"
              >
              Open</v-btn>
            <v-btn
              color="green darken-1"
              outline
              v-on:click="changeStatus('resolved')"
              v-if="conversation.status=='open'"
              >
              Resolve</v-btn>
            <v-btn
              color="red darken-2"
              outline
              v-on:click="changeStatus('closed')"
              v-if="conversation.status=='open'"
              >
              Close</v-btn>
          </div>
          <Chat :tweets="conversation.tweets" />
        </div>
      </v-flex>

      <v-flex d-flex xs12 sm6 md4 elevation-0>
        <div class="userinfo-container">
          <UserInfo
            :v-if="currentUser"
            :user="currentUser"
            :allTopics="allTopics"
            :topics="topics"
            :suggested="suggestedTopic"
            />
        </div>
      </v-flex>
    </v-layout>
  </v-container>
</v-content>

</template>


<script>

import axios from 'axios';
import UserInfo from '@/components/UserInfo.vue';
import Chat from '@/components/Chat.vue';

export default {
  name: 'conversation',
  components: {
    UserInfo,
    Chat,
  },
  data() {
    return {
      conversation: {},
      currentUser: {},
      topics: [],
      allTopics: [],
      suggestedTopic: '',
      changingStatus: false,
    };
  },
  computed: {
    conversationId() {
      return this.$route.params.ticketId;
    },
    screenName() {
      return this.$route.params.screenName;
    },
  },
  methods: {
    remove(item) {
      this.topics.splice(this.chips.indexOf(item), 1);
      this.topics = [...this.chips];
    },
    getTweets() {
      const url = `/api/conversations/${this.conversationId}`;
      return axios.get(url)
        .then((response) => {
          this.conversation = response.data;
          this.currentUser = this.conversation.tweets[0].user;
          this.topics = this.conversation.topics;
          // this.topics.push(this.conversation.suggested_topic + ' (*) ')
          // this.suggestedTopic = this.conversation.suggested_topic

          console.log('fetched', this.conversations.tweets.length, 'tweets');
        });
    },

    changeStatus(newState) {
      const url = `/api/conversations/${this.conversationId}/changeStatus?status=${newState}`;
      this.changingStatus = true;
      axios.get(url)
        .then((_) => {
          console.log('changed status');
          this.conversation.status = newState;
          this.changingStatus = false;
        });
    },

    getAllTopics() {
      const url = `/api/${this.screenName}/topics`;
      return axios.get(url)
        .then((response) => {
          this.allTopics = response.data;
        });
    },
  },
  created() {
    this.getAllTopics()
      .then(this.getTweets());
  },
};
</script>


<style scoped>
.content-padding, .container-padding {
    padding-bottom: 0 !important;
}
.container-padding {
    padding-top: 5px !important;
    padding-right: 10px !important;
    padding-left: 10px !important;
}

.chat-container, .userinfo-container {
    background-color: white;
    padding: 10px 5px 5px 10px;
    border-radius: 5px;
    height: auto;
    border: 1px solid #dedede;
    height: calc(100vh - 5em);
    overflow: scroll;
}

.userinfo-container {
    height: calc(100vh - 5em);
    padding: 10px;
    max-height: calc(100vh - 5em);
    overflow: scroll;
    position: fixed;
}

.no-border {
    border: none;
    min-height: calc(100vh - 5em);
    overflow: scroll;
}

.chat-controls {
    margin-right: 25px;
    padding-bottom: 5px;
    display: flex;
    justify-content: flex-end;
    border-bottom: 1px solid #ddd;
}

.chat-controls .v-toolbar {
    z-index: 100;
}

.combobox {
    margin-top: 5px;
}

</style>
