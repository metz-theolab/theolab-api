<template>
    <BContainer>

        <BRow>
            <BButton @click="modal = !modal" variant="outline-primary" pill class="m-2"> Add a new tradition </BButton>
            <BModal v-model="modal" title="Add new tradition" @ok="createTradition()">

                <BForm @submit="createTradition">
                    <BFormGroup id="input-group-1" label="Tradition name:" label-for="input-1">
                        <BFormInput id="input-1" v-model="newtraditionname" placeholder="Enter tradition name"
                            required />
                        <BFormCheckbox id="checkbox-1" v-model="newtraditionpublic" name="checkbox-1" value=true
                            unchecked-value=false>
                            Make tradition public
                        </BFormCheckbox>
                    </BFormGroup>
                </BForm>
            </BModal>
        </BRow>

        <div class="row">
            <div class="col">
                <BRow>
                    <BCard v-for:="tradition in traditions" :key="tradition.name" :title="tradition.name"
                        style="max-width: 15rem;">
                        <BCardText>
                            {{ tradition.name }}
                            <br/>
                            <span class="muted">
                                Owner: {{ tradition.created_by }}
                            </span>
                        </BCardText>
                        <router-link :to="{ path: '/tradition/' + tradition.name }">
                            <BButton variant="primary">Explore</BButton>
                        </router-link>
                        <BButton variant="primary" @click="deleteTradition(tradition)">Delete</BButton>
                        <BButton @click="addusermodal = !addusermodal" variant="primary" class="m-2"> Share</BButton>
                        <BModal v-model="addusermodal" title="Add new user" @ok="addUser(tradition)" >

                            <BForm @submit="createFolio">
                                <BFormGroup id="input-group-1" label="Username:" label-for="input-1">
                                    <BFormInput id="input-1" v-model="username" placeholder="Enter username" required />
                                </BFormGroup>
                            </BForm>
                        </BModal>
                    </BCard>
                </BRow>
            </div>
        </div>


    </BContainer>

</template>

<script>

export default {
    name: 'TraditionMenu',
    data() {
        return {
            traditions: null,
            newtraditionname: '',
            newtraditionpublic: false,
            modal: false,
            addusermodal: false,
            username: ''
        }
    },
    methods: {
        addUser(tradition) {
            this.axios
                .post('/permissions/' + tradition.name + '/' + this.username,
                    {
                    }
                )
                .then(response => response.status == 201 ? alert("Successfully added user" + this.username) : alert("Failed to add user"));
        },
        createTradition() {
            this.axios
                .post('/' + this.newtraditionname,
                    {
                        note: this.newtraditionname,
                        is_public: this.newtraditionpublic
                    }
                )
                .then(response => console.log("Successfully posted tradition"));
            window.location.reload();
        },
        deleteTradition(tradition) {
            this.axios
                .delete('/' + tradition.name)
                .then(response => console.log("Successfully deleted tradition"));
            window.location.reload();
        }
    },
    mounted() {
        console.log(this.axios.defaults.baseUrl);
        this.axios
            .get('/traditions')
            .then(response => (this.traditions = response.data))
    }
}
</script>