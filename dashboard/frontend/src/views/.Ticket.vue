<template>
<v-app>
  
  <ConversationList></ConversationList>
  <UserInfo></UserInfo>
  
  <v-content app>
    <div>
      Hello world
    </div>
  </v-content>
  
</v-app>
</template>


<script>
import ConversationList from '../components/ticket/ConversationList.vue'
import UserInfo from '../components/ticket/UserInfo.vue'
import ChatContainer from '../components/ticket/ChatContainer.vue'

export default {
  components: {
    ConversationList,
    UserInfo,
    ChatContainer,
  },
  data() {
    return {
      displayName: 'Ola Supports',
      username: 'himanshub16',
      screenName: 'ola_supports',

      conversations: [
        { icon: 'dashboard', title: 'first conversation' },
        { icon: 'gavel', title: 'second conversation' },
      ],
    };
  },
};
</script>
