<template>
<v-app>
  <v-toolbar app :clipped-left="clipped">
    <router-link to="/dashboard">
      <v-toolbar-title v-text="orgName"></v-toolbar-title>
    </router-link>
    <v-spacer></v-spacer>
    <v-menu offset-y>
      <v-btn slot="activator" outline>
        <span v-text="agentName"></span>
        <v-icon>keyboard_arrow_down</v-icon>
      </v-btn>
      <v-list>
        <v-list-tile @click="logout()">
          <v-list-tile-title>Log out</v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>
  </v-toolbar>

  <router-view />

</v-app>
</template>


<script>
export default {
  name: 'App',
  data() {
    return {
      orgName: 'Ola Support',
      agentName: 'Himanshu Shekhar',
    };
  },
  methods: {
    logout() {
      console.log('Logging out');
      // alert('Logging out')
    },
  },
};
</script>
