<template>
<v-jumbotron
  :gradient="gradient"
  dark
  class="fill-the-screen"
  >
  <v-container fill-height>
    <v-layout align-center>
      <v-flex text-center>
        <img src="@/assets/logo.png" alt="Vuetify.js" class="mb-5">
      </v-flex>
      <v-flex>
        <h2 class="display-3">{{ appName }}</h2>
        <p class="display-1">
          Never dissatisfy a customer on Twitter.
        </p>
        <span v-for="each in screenNames" :key="each.screenName">

          <router-link :to="{ name: 'dashboard', params: {screenName: each.screenName }}">
            <v-btn outline>
              <span>{{ each.name }}</span>
            </v-btn>
          </router-link>

        </span>

      </v-flex>
    </v-layout>
  </v-container>
</v-jumbotron>
</template>


<script>

const gradients = [
  '#509BFB, #3EE5FB',
  '#FFA7E7, #EA6362',
  '#17EAD9, #6078EA',
  '#23BCBB, #45E994',
  '#FFDEA7, #EA6362',
  '#9B3CB7, #FF396F',
  '#004B91, #78CC37',
  '#F83600, #F9D423',
  '#38B8F2, #843CF7',
  '#E35C67, #381CE2',
  '#EFBFD5, #9D61FD',
  '#45E0A7, #D5E969',
  '#D73E68, #FBC79A',
  '#8137F7, #F6AB3E',
  '#FCE38A, #F38181',
  '#F54EA2, #FF7676',
  '#622774, #C53364',
  '#3a67b0, #3bd2f3',
  '#3e9fb5, #69d1cf',
  '#aaafe3, #dd8ce8',
  '#7117EA, #EA6060',
  '#3FFDE0, #8927EA',
  '#42E695, #3BB2B8',
  '#F02FC2, #6094EA',
  '#65799B, #5E2563',
  '#184E68, #57CA85',
  '#5B247A, #1BCEDF',
  '#A8EDEA, #FED6E3',
  '#A5C0EE, #FBC5EC',
  '#6A11CB, #2575FC',
  '#FFB199, #FF0844',
  '#F9F047, #0FD850',
  '#7742B2, #FD8BD9',
  '#AC32E4, #4801FF',
  '#C7EAFD, #E8198B',
  '#F43B47, #453A94',
  '#FFF1EB, #ACE0F9',
  '#D1FDFF, #FDDB92',
  '#00DBDE, #FC00FF',
  '#FF57B9, #A704FD',
  '#B3EB50, #429421',
  '#E3E3E3, #5D6874',
  '#0FF0B3, #036ED9',
  '#FC0D1B, #FC23DA',
  '#7556A1, #A14A93, #E41F7C',
  '#FADF38, #81C375, #56C2C5',
  '#FABA36, #E84A75, #81519E',
  '#3BFEE5, #2CC3ED, #176BED',
  '#7D38FB, #C02EC4, #E8207B',
  '#FDBE2F, #E64778, #8927EA',
];

const randomBg = () => gradients[Math.floor((Math.random() * 1000) % gradients.length)];
export default {
  data() {
    return {
      appName: 'Puddle',
      gradient: `to right, ${randomBg()}`,
      screenNames: [
        { name: 'Ola', screenName: 'ola_supports' },
        { name: 'Uber India', screenName: 'UberINSupport' },
        { name: 'Flipkart', screenName: 'flipkartsupport' },
        { name: 'Gmail', screenName: 'gmail' },
      ],
    };
  },
};
</script>


<style scoped>
  .fill-the-screen {
    background-color: light-blue;
    border: 1px solid black;
    min-height: 100vh;
    height: 100vh;
  }
</style>
