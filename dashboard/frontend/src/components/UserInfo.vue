<template>
<v-container fluid
             v-if="user.id"
             >
  <v-layout column align-center>
    
    <!-- avatar -->
    <v-flex>
      <v-avatar :size="100">
        <img :src="user.profile_image_url_http || user.profile_image_url" :alt="user.name">
      </v-avatar>
    </v-flex>
    
    <!-- username -->
    <v-flex class="title">
      {{ user.name }}
      <v-icon
        v-if="user.verified"
        title="Verified" class="verified-badge" small color="blue"
        >
        verified_user
      </v-icon>
    </v-flex>
    
    <!-- screen-name -->
    <v-flex class="body-2 grey--text lighten-1">
      <a :href="'https://twitter.com/' + user.screen_name" target="_blank">
        @{{ user.screen_name }}
      </a>
    </v-flex>
    
    <!-- bio -->
    <v-flex>
      {{ user.description }}
    </v-flex>
    
    <!-- location -->
    <v-flex v-show="user.location">
      <v-icon>location_on</v-icon>
      {{ user.location }}
    </v-flex>
    
    <!-- stats -->
    <v-flex>
      <table>
        <tr>
          <td class="subheading indigo--text darken-4">{{ created_at }} &nbsp; </td>
          <td class="grey--text lighten-1">on Twitter</td>
        </tr>
        <tr>
          <td class="subheading indigo--text darken-4">{{ issue_count }}</td>
          <td class="grey--text lighten-1">Issues so far</td>
        </tr>
        <tr>
          <td class="subheading indigo--text darken-4">{{ user.friends_count }} &nbsp; </td>
          <td class="grey--text lighten-1">Following</td>
        </tr>
        <tr>
          <td class="subheading indigo--text darken-4">{{ user.followers_count }} &nbsp; </td>
          <td class="grey--text lighten-1">Followers</td>
        </tr>
        <tr>
          <td class="subheading indigo--text darken-4">{{ user.statuses_count }} &nbsp; </td>
          <td class="grey--text lighten-1">Tweets</td>
        </tr>
      </table>
    </v-flex>
    
    <!-- ticket-actions -->
    <v-flex style="align-self: flex-end">
      <div class="title blue--text darken-4 topics-heading">
        Topics
      </div>

      <v-progress-circular
        indeterminate
        color="primary"
        v-if="updatingTopics"
        :size="50"
        ></v-progress-circular>

      <v-combobox
        v-else
        v-model="_topics"
        :items="allTopics"
        label="Topics"
        chips
        clearable
        solo
        multiple
        light
        class="combobox"
        >

        <template slot="selection" slot-scope="data"
                  >
          <v-chip
            :selected="data.selected"
            small
            color="blue darken-2"
            text-color="white"
            @input="remove(data.item)"
            >
            <small>
              {{ data.item }}
            </small>
          </v-chip>
        </template>

      </v-combobox>

    </v-flex>
  </v-layout>
</v-container>
</template>

<script>
import axios from 'axios'
  
export default {
  // name: 'user-info',
  props: ['user', 'topics', 'allTopics'],
  data() {
    return {
      updatingTopics: false,
      issue_count: 0,
    }
  },
  methods: {
    remove(item) {
      this.topics.splice(this.chips.indexOf(item), 1);
      this.topics = [...this.chips];
    },
    
    getIssueCount: function() {
      let url = `/api/${this.screenName}/n_issues/${this.userScreenName}`
      console.log(url)
      axios.get(url)
        .then((response) => {
          this.issue_count = response.data.count
        })
    },
  },
  
  computed: {
    _topics: function() {
      return this.topics
    },

    created_at() {
      const t = new Date();
      const d = new Date(this.user.created_at);
      const diff = {
        year: t.getUTCFullYear() - d.getUTCFullYear(),
        month: t.getUTCMonth() - d.getUTCMonth(),
        day: t.getUTCDate() - d.getUTCDate(),
      };
      if (diff.year > 0) {
        return `${diff.year} years`;
      } else if (diff.month > 0) {
        return `${diff.month} months`;
      }
      return `${diff.day} days`;
    },
    
    screenName: function() {
      return this.$route.params.screenName
    },
    
    conversationId: function() {
      return this.$route.params.ticketId
    },
    
    userScreenName: function() {
      return this.user.screen_name
    },

    areArraysSame: function(A, B) {
      let s = new Set(A)
      let s2 = new Set(B)
      s2.forEach(i => s.delete(i))
      return s2.size == 0
    },
    
  },
  
  watch: {
    '_topics': function(newval, oldval) {
      let url = `/api/conversations/${this.conversationId}/topics`
      console.log('requesting to update topics')
      this.updatingTopics = true
      axios({
        method: 'PUT',
        url: url,
        data: {
          topics: newval
        },
      })
        .then(() => {
          this.updatingTopics = false
        })
    },
  },
  
  created() {
    this.getIssueCount()
  }
};
</script>


<style scoped>
a {
    text-decoration: none;
}
table {
    font-weight: bold;
}
.verified-badge {
    margin-bottom: 0.3ch;
}
.v-chip {
    padding: 0;
}
.topics-heading {
    text-align: center;
    width: 100%;
    margin: 10px 0;
}
</style>
