<template>
  <div v-if="strategies && strategies.length !== 0">
    <v-card-title class="justify-center py-2 body-1 text--secondary">
      <v-divider class="mx-4"></v-divider>
      Sign in with
      <v-divider class="mx-4"></v-divider>
    </v-card-title>
    <v-card-text class="pb-5">
      <template v-for="s in strategies">
        <v-col
          :key="s.name"
          cols="12"
          class="text-center py-1 my-0"
          @click="trackSignIn(s.name)"
        >
          <v-btn
            dark
            block
            :color="s.color"
            :href="`${s.url}?appId=${appId}&challenge=${challenge}${
              suuid ? '&suuid=' + suuid : ''
            }${inviteId ? '&inviteId=' + inviteId : ''}`"
          >
            <v-icon small class="mr-5">{{ s.icon }}</v-icon>
            {{ s.name }}
          </v-btn>
        </v-col>
      </template>
    </v-card-text>
  </div>
</template>
<script>
export default {
  name: 'AuthStrategies',
  props: {
    strategies: {
      type: Array,
      default: () => []
    },
    appId: {
      type: String,
      default: () => null
    },
    challenge: {
      type: String,
      default: () => null
    },
    suuid: {
      type: String,
      default: () => null
    }
  },
  data() {
    return {
      inviteId: null
    }
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search)
    const inviteId = urlParams.get('inviteId')
    this.inviteId = inviteId
  },
  methods: {
    trackSignIn(strategyName) {
      this.$mixpanel.track('Log In', {
        isInvite: this.inviteId !== null,
        type: 'action',
        provider: strategyName
      })
    }
  }
}
</script>
