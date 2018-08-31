<template>
<v-content
  fixed
  >
  <v-container fluid fill-height
               >
    <v-layout column fill-height>
      <v-container fluid>
        <v-layout row justify-space-around>
          <v-flex md2
                  v-for="metric in metrics">
            <v-card class="metric-card">
              <div class="display-3 value">
                {{ metric.count }}
              </div>
              <div class="subheading name">
                {{ metric.name }}
              </div>
            </v-card>
          </v-flex>
        </v-layout>
      </v-container>


      <v-layout row justify-center>
        <v-flex md2>
          <v-overflow-btn
            :items="topics"
            :value="(current_topic.name != null) ? current_topic.name : null"
            label="Topic"
            class="topic-dropdown"
            @change="updateCurrentTopic($event)"
            ></v-overflow-btn>
        </v-flex>

        <v-flex md2
                class="current_topic_count">
          <v-card>
            <v-card-title
              v-if="current_topic.name">
              {{ current_topic.count }} issues here
            </v-card-title>
            <v-card-title
              v-else
              >
              Select topic (left) to filter
            </v-card-title>
          </v-card>
        </v-flex>
      </v-layout>

      <v-container fluid>
        <v-layout row justify-space-around>

          <v-data-table
            hide-actions
            :headers="conversation_headers"
            expand
            :items="conversations"
            item-key="_id.$oid"
            >
            <template slot="headers" slot-scope="props">
              <tr>
                <th
                  v-for="header in props.headers"
                  :key="header.name"
                  >
                  {{ header.name }}
                </th>
              </tr>
            </template>
            <template slot="items" slot-scope="props">
              <tr @click="props.expanded = !props.expanded">
                <td>
                  <router-link :to="{ name: 'ticket', params: { ticketId: props.item._id.$oid } }">
                    <v-icon>open_in_browser</v-icon>
                  </router-link>
                </td>
                <td>{{ props.item.tweet.created_at }}</td>
                <td>@{{ props.item.tweet.user.screen_name }}
                // {{ props.item.tweet.user.screen_name }}</td>
                <td>{{ props.item.n_messages }}</td>
                <td>{{ props.item.topics[0] }}</td>
                <td>{{ trimText(props.item.tweet.full_text) }}</td>
              </tr>
            </template>
            <tempate slot="expand" slot-scope="props">
              <v-card flat>
                <v-card-text>Poof</v-card-text>
              </v-card>
            </tempate>
          </v-data-table>
        </v-layout>
      </v-container>
    </v-layout>

  </v-container>
</v-content>

</template>


<script>
import axios from 'axios';

export default {
  name: 'dashboard',
  data() {
    return {
      conversations: [],
      conversation_headers: [
        { name: 'visit' },
        { name: 'date' },
        { name: 'username' },
        { name: 'category' },
        { name: 'text' },
      ],
      metrics: [
        {
          name: 'open',
          count: 432,
        },
        {
          name: 'due',
          count: 453,
        },
        {
          name: 'closed',
          count: 411,
        },
        {
          name: 'created today',
          count: 123,
        },
      ],

      topics: null,
      current_topic: {
        name: null,
        count: 0,
      },
    };
  },
  computed: {
    screenName() {
      return this.$route.params.screenName;
    },
  },
  methods: {
    updateCurrentTopic(new_topic) {
      this.current_topic.name = new_topic;
      console.log('current topic is', new_topic);
      this.getConversations();
    },
    getConversations() {
      let url = `/api/${this.screenName}/conversations`;
      const topic = this.current_topic.name;
      if (topic) { url += `?topic=${topic}`; }
      axios.get(url)
        .then((response) => {
          this.conversations = response.data.conversations;
          this.current_topic.count = response.data.count;
        });
    },
    getTopics() {
      const url = `/api/${this.screenName}/topics`;
      axios.get(url)
        .then((response) => {
          this.topics = response.data;
        });
    },
    trimText(text) {
      const maxLen = 50;
      if (text.length < maxLen) { return text; }
      return `${text.substr(0, maxLen)}...`;
    },
  },
  created() {
    this.getTopics();
    this.getConversations();
  },
};
</script>

<style scoped>
a {
    text-decoration: none;
}

.metric-card {
    padding: 5px 10px;
    text-align: center;
}
.metric-card .value {

}
.metric-card .name {
    text-transform: capitalize;
    border-top: 1px solid #ddd;
}

.topic-dropdown {
    width: 200px;
    margin-bottom: -25px;
}
.current_topic_count {
    margin-top: 10px;
}
</style>
