<template>
  <v-ons-page>
    <v-ons-tabbar :index.sync="activeIndex">
      <template slot="pages">
        <main-page ref="mainPage" @push-page="pushPage($event)"></main-page>
        <account-page @push-page="pushPage($event)"></account-page>
      </template>

      <v-ons-tab
        v-for="(tab, i) in tabs"
        :key="tab.key"
        :icon="tabs[i].icon"
        :label="tabs[i].label"
        :badge="tabs[i].badge"
      ></v-ons-tab>
    </v-ons-tabbar>
  </v-ons-page>
</template>

<script>
import mainPage from "~/components/app/pages/mainPage";
import accountPage from "~/components/app/pages/accountPage";
import registerIdmPage from "~/components/app/pages/registerIdmPage";
import { mapState } from "vuex";

export default {
  middleware: ["auth"],
  data() {
    return {
      activeIndex: 0,
      tabs: [
        {
          icon: "ion-home",
          label: "Home",
          key: "homePage"
        },
        {
          icon: "ion-person",
          label: "Account",
          key: "accountPage"
        }
      ]
    };
  },
  methods: {
    pushPage(event) {
      this.$emit("push-page", event);
    }
  },
  computed: {
    ...mapState("app/register-idm", ["idm"])
  },
  components: {
    mainPage,
    accountPage
  },
  layout: "app",

  mounted() {
    // IDM登録のタスクがあれば
    if (this.idm) {
      this.$emit("push-page", registerIdmPage);
    }
  }
};
</script>
