<template>
<div>


  <router-view :key="this.$route.params.ticketId" />
  <ConversationList :conversationId="conversationId" />
  <!-- <conversation-list /> -->

  </div>
</template>


<script>
import ConversationList from '@/components/ConversationList.vue';
import ChatContainer from '@/views/ChatContainer.vue';

export default {
  name: 'conversation',
  components: {
    ConversationList,
  },
  data() {
    return {
      conversationId: this.$route.params.ticketId,
    };
  },
};
</script>
