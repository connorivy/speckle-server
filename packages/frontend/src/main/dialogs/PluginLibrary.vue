<template>
  <v-card>
    <v-sheet color="primary">
      <v-toolbar color="primary" dark flat>
        <v-app-bar-nav-icon style="pointer-events: none">
          <v-icon>mdi-bookshelf</v-icon>
        </v-app-bar-nav-icon>
        <v-toolbar-title>Search the Plugin Library</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="$emit('close')"><v-icon>mdi-close</v-icon></v-btn>
      </v-toolbar>
      <v-card-text class="mt-0 mb-0 px-2" style="padding-bottom: 0px;">
        <v-text-field
          v-model="pluginName"
          dark
          filled
          rounded
          hint="Search for my plugin, rainbow structure"
          style="color: blue"
          prepend-inner-icon="mdi-magnify"
          @keyup="populatePluginList()"
        ></v-text-field>
      </v-card-text>
      <v-card-text class="px-2" style="padding-top: 0px;">
        <v-btn
          text
          rounded
          @click="runPlugin()"
        >
          <v-icon>mdi-folder-open</v-icon>
          run existing plugin
        </v-btn>
      </v-card-text>
    </v-sheet>
    <v-sheet
      v-if="stream"
      :xxxclass="`${!$vuetify.theme.dark ? 'grey lighten-4' : 'grey darken-4'}`"
    >
      <v-toolbar
        v-for="item in searchResultsSubset"
        :key="item.name"
        flat
        class="transparent"
      >
        <v-app-bar-nav-icon style="pointer-events: none">
          <v-img
            class="hover-tada mt-2"
            width="20"
            src="@/assets/specklebrick.png"
            style="display: inline-block"
          />
        </v-app-bar-nav-icon>
        <v-toolbar-title>{{ item.name }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          text
          rounded
          :disabled="stream.role !== 'stream:owner'"
          @click="downloadPlugin(item.name, item.version)"
        >
          Download
        </v-btn>
      </v-toolbar>
    </v-sheet>
  </v-card>
</template>
<script>
import { flow, map, sortBy } from 'lodash/fp'

export default {
  name: 'pluginLibrary',
  components: {
    UserAvatar: () => import('@/main/components/common/UserAvatar'),
    StreamInviteDialog: () => import('@/main/dialogs/StreamInviteDialog')
  },
  props: {
    stream: {
      type: Object,
      default: () => null
    }
  },
  data() {
    return {
      pluginName : '',
      searchResults : null,
      searchResultsSubset: [],
      // response: null,
      swapPermsLoading: false
    }
  },
  created() {
    const URL = 'https://registry.npmjs.com/-/v1/search?from=0&size=500&text=keywords:cerebro-plugin';
    console.log(URL)
    this.searchResults = fetch(URL)
      .then(response => response.json())
      .then(json => flow(
        sortBy(p => -p.score.detail.popularity),
        map(p => ({
          name: p.package.name,
          version: p.package.version,
          description: p.package.description,
          homepage: p.package.links.homepage,
          repo: p.package.links.repository
        }))
      )(json.objects)
    )
    this.populatePluginList()
  },
  computed: {
    streamUrl() {
      return `${window.location.origin}/streams/${this.$route.params.streamId}`
    },
    myId() {
      return localStorage.getItem('uuid')
    },
  },
  mounted() {
    this.$mixpanel.track('Share Stream', {
      type: 'action',
      location: this.$route.name
    })
  },
  methods: {
    async populatePluginList() {
      this.searchResultsSubset = []
      const value = await this.searchResults
      for (var index in value) {
        if (value[index]['name'].slice(0,8 + this.pluginName.length) == 'cerebro-' + this.pluginName) {
          // console.log(value[index]['name'])
          this.searchResultsSubset.push(value[index])
          if (this.searchResultsSubset.length >= 4) break
        }
      }
    },

    downloadPlugin(name, version) {
      window.open(`https://registry.npmjs.org/${name}/-/${name}-${version}.tgz`, "_blank");
    },

    // right now you have to navigate to the javascript file to run your plugin
    // and you have to redo that everytime you want to run it. It's a bad system and its just for demo
    // I think it makes sense to move the plugin managment to the 'speckle manager' desktop app
    // so we can save plugins to a known location on the user's machine and access them from there 
    // so there is no need for the user to open a file explorer
    runPlugin() {
      var script = document.getElementById("pluginScript");

      // define script if null
      if (!script) {
        script = document.createElement('script')
        script.id = 'pluginScript'
        // script.async = true;
        document.body.appendChild(script)
      }

      // create file dialog element
      var input = document.createElement('input')
      input.type = 'file'
      input.onchange = e => { 
        // getting a hold of the file reference
        var file = e.target.files[0]

        // read file
       var reader = new FileReader();
       reader.readAsText(file,'UTF-8');

       // when file is done reading...
        reader.onload = readerEvent => {
          var content = readerEvent.target.result;
          script.innerHTML = content;

          // try to run the user's plugin
          try {
            pluginMain(window.__viewer, this.$store)
            console.log('plugin ran sucessfully')
          } catch (error) {
            console.log('Plugin failed with error ', error)
          }
        }
      }
      input.click();
      this.$emit('close')
      return false;
    },
  }
}
</script>
