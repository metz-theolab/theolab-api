<template>
    <BContainer>
        <!-- The current route is accessible as $route in the template -->
        You are viewing the manuscripts of {{ $route.params.tradition }}

        <BRow>
            <BButton @click="modal = !modal" variant="outline-primary" pill> Add a new manuscript </BButton>
            <BModal v-model="modal" title="Add new tradition" @ok="createManuscript()">

                <BForm @submit="createManuscript">
                    <BFormGroup id="input-group-1" label="Manuscript name:" label-for="input-1">
                        <BFormInput id="input-1" v-model="newmanuscriptname" placeholder="Enter manuscript name"
                            required />
                    </BFormGroup>
                </BForm>
            </BModal>
        </BRow>
        <BRow>

            <BCard class="m-2" v-for:="manuscript in manuscripts" :key="manuscript.name" :title="manuscript.name"
                style="max-width: 15rem;">
                <BCardText>
                    Manuscript {{ manuscript.name }}
                </BCardText>
                
                <router-link :to="{ path: '/tradition/' + tradition + '/' + manuscript.name}">
                    <BButton variant="primary" class="m-2">Explore</BButton>
                </router-link>
                <BButton variant="primary" @click="deleteManuscript(manuscript)">Delete</BButton>
            </BCard>
        </BRow>
    </BContainer>
</template>

<script>

export default {
    name: 'ManuscriptMenu',
    data() {
        return {
            modal: false,
            manuscripts: null,
            tradition: this.$route.params.tradition
        }
    },
    methods: {
        createManuscript() {
            this.axios
                .post('/' + this.tradition + '/' + this.newmanuscriptname,
                    {
                        note: this.newmanuscriptname,
                    }
                )
                .then(response => console.log("Successfully created manuscript"));
            window.location.reload();
        },
        deleteManuscript(manuscript) {
            this.axios
                .delete('/' + this.tradition + '/' + manuscript.name)
                .then(response => console.log("Successfully deleted manuscript"));
            window.location.reload();
        }
    },
    mounted() {
        console.log(this.axios.defaults.baseUrl);
        this.axios
            .get('/traditions/' + this.tradition)
            .then(response => (this.manuscripts = response.data))
    }
}
</script>