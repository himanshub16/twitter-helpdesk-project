<template>
  <v-navigation-drawer
    fixed
    clipped
    app
    >
    <v-list
      dense
      >
      <v-list-tile
        value="true"
        v-for="conv in conversations"
        :key="conv._id.$oid"
        >
        <router-link :to="{ name: 'ticket', params: { ticketId: conv._id.$oid } }">
          <v-list-tile-action>
            <v-avatar :size="30">
              <img :src="conv.tweet.user.profile_image_url_http || conv.tweet.user.profile_image_url"
                   :alt="conv.tweet.user.screen_name[0]">
            </v-avatar>
          </v-list-tile-action>
        </router-link>
        <router-link
          :to="{ name: 'ticket', params: { ticketId: conv._id.$oid } }"
          >
          <v-list-tile-content>
            <v-list-tile-title
              v-text="trimText(conv.tweet.processed_text)"
              >
            </v-list-tile-title>
          </v-list-tile-content>
        </router-link>
      </v-list-tile>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      conversations: [],
    };
  },
  computed: {
    screenName() {
      return this.$route.params.screenName;
    },
  },
  methods: {
    getConversations() {
      const url = `http://localhost:5000/api/${this.screenName}/conversations`;
      axios.get(url)
        .then((response) => {
          this.conversations = response.data.conversations;
          console.log('fetched', this.conversations.length, 'convs');
        });
    },
    trimText(text) {
      const maxLen = 20;
      if (text.length < maxLen) { return text; }
      return `${text.substr(0, maxLen)}...`;
    },
  },
  created() {
    this.getConversations();
  },
};
</script>


<style scoped>
  a {
      text-decoration: none;
  }
</style>
