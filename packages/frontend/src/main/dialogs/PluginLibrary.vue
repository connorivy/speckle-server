<template>
  <v-card>
    <v-sheet color="primary">
      <v-toolbar color="primary" dark flat>
        <v-app-bar-nav-icon style="pointer-events: none">
          <v-icon>mdi-share-variant</v-icon>
        </v-app-bar-nav-icon>
        <v-toolbar-title>Search the Plugin Library</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="$emit('close')"><v-icon>mdi-close</v-icon></v-btn>
      </v-toolbar>
      <v-card-text class="mt-0 mb-0 px-2">
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
    </v-sheet>
    <v-sheet v-if="stream">
      <v-toolbar
        v-tooltip="
          `${
            stream.role !== 'stream:owner'
              ? 'You do not have the right access level (' +
                stream.role +
                ') to add collaborators.'
              : ''
          }`
        "
        flat
      >
        <v-app-bar-nav-icon style="pointer-events: none">
          <v-icon>mdi-account-group</v-icon>
        </v-app-bar-nav-icon>
        <v-toolbar-title>
          Collaborators
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          text
          rounded
          :disabled="stream.role !== 'stream:owner'"
          @click="install()"
        >
          Manage
        </v-btn>
      </v-toolbar>
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
          @click="install(item.name)"
        >
          Install
        </v-btn>
      </v-toolbar>
      <stream-invite-dialog
        ref="streamInviteDialog"
        :stream-id="$route.params.streamId"
      />
    </v-sheet>
  </v-card>
</template>
<script>
import gql from 'graphql-tag'
import { COMMON_STREAM_FIELDS } from '@/graphql/streams'
import { flow, map, sortBy } from 'lodash/fp'
import os from 'os'

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
      // console.log(this.pluginName)
      const value = await this.searchResults
      // console.log(value)
        for (var index in value) {
          // console.log(value[index]['name'].slice(0,8 + this.pluginName.length))
          if (value[index]['name'].slice(0,8 + this.pluginName.length) == 'cerebro-' + this.pluginName) {
            // console.log(value[index]['name'])
            this.searchResultsSubset.push(value[index])
            if (this.searchResultsSubset.length >= 4) break
          }
        }
      // console.log(this.searchResultsSubset)
      // const electronApp = remote ? remote.app : app
      // const pluginsPath = path.join(electronApp.getPath('userData'), 'plugins')
      // console.log(electronApp, pluginsPath)
      console.log(os.homedir())
      console.log(process.env.LOCALAPPDATA)
    },
    installPlugin() {
      const script = document.createElement('script');
      // script.src = scriptUrl; // fully qualified path to the loaded script

      script.async = true;
      document.body.appendChild(script);
    },
    /**
     * Install npm package
     * @param  {String} name Name of package in npm registry
     *
     * @param  {Object} options
     *             version {String} Version of npm package. Default is latest version
     *             middleware {Function<Promise>}
     *               Function that returns promise. Called when package's archive is extracted
     *               to temp folder, but before moving to real location
     * @return {Promise}
     */
    install(name, options = {}) {
      // console.log(window.__viewer)
      // console.log(this.$store)

      var v = window.__viewer
      var maxLength = 0
      var maxLengthId = 0
      for (var index in v.sceneManager.sceneObjects.allSolidObjects.children) {
        // console.log(v.sceneManager.sceneObjects.allSolidObjects.children[index].userData.baseLine)
        var length = this.getLength(v.sceneManager.sceneObjects.allSolidObjects.children[index].userData)
        if (length > maxLength) {
          maxLength = length
          maxLengthId = v.sceneManager.sceneObjects.allSolidObjects.children[index].userData.id
        }
      }

      // // v.applyFilter({filterBy: {id : maxLengthId}, ghostOthers: true})
      this.$store.commit('isolateObjects', {
          filterKey: '__parents',
          filterValues: [maxLengthId]
        })
      console.log(maxLength, maxLengthId)

      // state.appliedFilter = {filterBy: {'speckle_type': 'Objects.Geometry.Line'}, ghostOthers: true }
      // viewer.applyFilter({filterBy: {'speckle_type': 'Objects.Geometry.Line'}, ghostOthers: true })

      // const dir = '/'
      // const API_BASE = 'http://registry.npmjs.org/'
      // let versionToInstall
      // const version = options.version || null
      // const middleware = options.middleware || (() => Promise.resolve())
      // console.group('[npm] Install package', name)
      // return fetch(`${API_BASE}${name}`)
      //   .then(response => console.log(response))
      //   .then((json) => {
      //     versionToInstall = version || json['dist-tags'].latest
      //     console.log('Version:', versionToInstall)
      //     return installPackage(
      //       json.versions[versionToInstall].dist.tarball,
      //       path.join(dir, 'node_modules', name),
      //       middleware
      //     )
      //   })
      //   .then(() => {
      //     const json = getConfig()
      //     json.dependencies[name] = versionToInstall
      //     console.log('Add package to dependencies')
      //     setConfig(json)
      //     console.groupEnd()
      //   })
      //   .catch((err) => {
      //     console.log('Error in package installation')
      //     console.log(err)
      //     console.groupEnd()
      //   })
    },
    getLength(obj) {
      // console.log(obj)
      if (obj.hasOwnProperty('baseLine')) {
        return Math.sqrt( (obj.baseLine.start.x - obj.baseLine.end.x )**2 + 
        (obj.baseLine.start.y - obj.baseLine.end.y )**2 + 
        (obj.baseLine.start.z - obj.baseLine.end.z )**2 )
      }
      return 0
    },
    installPackage(tarPath, destination, middleware) {
      console.log(`Extract ${tarPath} to ${destination}`)
      return new Promise((resolve, reject) => {
        const packageName = path.parse(destination).name
        const tempPath = `${os.tmpdir()}/${packageName}`
        console.log(`Download and extract to temp path: ${tempPath}`)
        https.get(tarPath, (stream) => {
          console.log(`STREAM`, stream)
          const result = stream
            // eslint-disable-next-line new-cap
            .pipe(zlib.Unzip())
            .pipe(tar.extract(tempPath, {
              map: formatPackageFile
            }))
          result.on('error', reject)
          result.on('finish', () => {
            middleware().then(() => {
              console.log(`Move ${tempPath} to ${destination}`)
              mv(tempPath, destination, err => err ? reject(err) : resolve())
            })
          })
        })
      })
    },
    copyToClipboard(e) {
      // this.$clipboard(e.target.value)
      // console.log(e.target.value)
      e.target.select()
      document.execCommand('copy')
    },
    goToStreamCollabs() {
      this.$router.push(`/streams/${this.$route.params.streamId}/collaborators`)
      this.$emit('close')
    },
    showStreamInviteDialog() {
      this.$refs.streamInviteDialog.show()
    },
    getIframeUrl() {
      const resourceId = this.$route.params.resourceId
      if (!resourceId) return null
      let base = `${window.location.origin}/embed?stream=${
        this.$route.params.streamId
      }&${this.$resourceType(resourceId)}=${this.$route.params.resourceId}`

      if (this.$route.query.overlay) {
        base += `&overlay=${this.$route.query.overlay}`
      }
      if (this.$route.query.c) {
        base += `&c=${encodeURIComponent(this.$route.query.c)}`
      }
      if (this.$route.query.filter) {
        base += `&filter=${encodeURIComponent(this.$route.query.filter)}`
      }

      return `<iframe src="${base}" width="600" height="400"></iframe>`
    },
    async changeVisibility() {
      this.swapPermsLoading = true

      const newIsPublic = !this.stream.isPublic
      try {
        await this.$apollo.mutate({
          mutation: gql`
            mutation editDescription($input: StreamUpdateInput!) {
              streamUpdate(stream: $input)
            }
          `,
          variables: {
            input: {
              id: this.$route.params.streamId,
              isPublic: newIsPublic
            }
          },
          optimisticResponse: {
            __typename: 'Mutation',
            streamUpdate: newIsPublic
          },
          update: (cache, { data: { streamUpdate: isSuccessFul } }) => {
            // Update stream public value in cache
            const normalizedId = `Stream:${this.stream.id}`
            const cachedStream = cache.readFragment({
              id: normalizedId,
              fragment: COMMON_STREAM_FIELDS
            })

            cache.writeFragment({
              id: normalizedId,
              fragment: COMMON_STREAM_FIELDS,
              data: {
                ...cachedStream,
                isPublic: isSuccessFul ? newIsPublic : !newIsPublic
              }
            })
          }
        })
      } catch (e) {
        this.$eventHub.$emit('notification', {
          text: e.message ? e.message : 'Something went wrong.'
        })
      }
      this.swapPermsLoading = false
    }
  }
}
</script>
