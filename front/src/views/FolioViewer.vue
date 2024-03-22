<template>
    Viewing content of folio : {{ $route.params.folio }} for manuscript : {{ $route.params.manuscript }} in tradition
    {{ $route.params.tradition }}

    <BRow>
        <BCol md="2">
            <BButton @click="Save()">
                Save
            </BButton>

        </BCol>

    </BRow>
    <BRow>
        <BCol lg="6">
            <BImg :src="getImageUrl(folioData.image_url)" fluid />
        </BCol>
        <BCol lg="6">
            <BRow>
                <BCol md="3">
                    <BFormCheckbox id="checkbox-1" v-model="editing" name="checkbox-1" value=editing
                        unchecked-value=not_editing>
                        Edit.
                    </BFormCheckbox>
                </BCol>
                <BCol md="3">
                    <BFormSpinbutton placeholder="1" v-model="createdcolumn" />
                    <BButton @click="addColumn">
                        Add
                    </BButton>
                </BCol>
                <BCol md="4">
                    Column:
                    <BFormSelect :options="columns" v-model="column" @change="getContent"></BFormSelect>
                </BCol>
            </BRow>

            <codemirror v-model="content" @change="sendData()" :disabled='editing != "editing"' />
        </BCol>
    </BRow>

</template>

<script>
import { defineComponent } from 'vue'
import { Codemirror } from 'vue-codemirror'


export default defineComponent({
    components: {
        Codemirror
    },
    created(){
        window.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
          // Prevent the Save dialog to open
          e.preventDefault();
          // Place your code here
          this.Save();
          alert("Saved content")}
        })
    },
    data() {
        return {
            folio: this.$route.params.folio,
            manuscript: this.$route.params.manuscript,
            tradition: this.$route.params.tradition,
            content: 'test',
            editing: "not_editing",
            column: 1,
            createdcolumn: 1,
            columns: [{ "value": 1, "text": 1 }],
            folioData: { "image_url": "placeholder.jpg" }
        }
    },
    methods: {
        getImageUrl(image) {
            return 'http://localhost:8000/static/' + image;
        },
        sendData() {
            if (this.editing == "editing") {
                this.ws.send(this.content);
            };
        },
        getColumns() {
            this.columns = [];
            this.axios
                .get('/traditions/' + this.tradition + '/' + this.manuscript + '/' + this.folio + '/columns/')
                .then(response => (response.data.forEach((element, index, array) => {
                    this.columns.push({ "value": element.position_in_folio, "text": element.position_in_folio })
                })));
        },
        addColumn() {
            this.axios
                .post('/' + this.tradition + '/' + this.manuscript + '/' + this.folio + '/' + this.createdcolumn,
                    {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }
                ).then(response => this.getColumns());
        },
        Save() {
            this.axios
                .post('/' + this.tradition + '/' + this.manuscript + '/' + this.folio + '/' + this.column + '/content',
                    {
                        content: this.content
                    }
                )
                .then(response => this.response.status == 200 ? alert("Successfully saved content") : alert("Error saving content"));
        },
        getContent() {
            this.axios
                .get('/traditions/' + this.tradition + '/' + this.manuscript + '/' + this.folio + '/' + this.column + '/content/')
                .then(response => (
                    this.content = response.data.content
                ));
        },
    },

    mounted() {
        this.ws = new WebSocket("ws://localhost:8000/wsedition/" + this.tradition + "/" + this.manuscript + "/" + this.folio);

        this.axios
            .get('/traditions/' + this.tradition + '/' + this.manuscript + '/' + this.folio)
            .then(response => (this.folioData = response.data));


        this.axios
            .get('/traditions/' + this.tradition + '/' + this.manuscript + '/' + this.folio + '/columns/')
            .then(response => (response.data.forEach((element, index, array) => {
                this.columns.push({ "value": element.position_in_folio, "text": element.position_in_folio })
            })));

        this.ws.onmessage = (evt) => {
            var obj = JSON.parse(evt.data);
            if (this.editing == "not_editing") {
                this.content = obj.message
            }
            else {
                console.log("Not editing anything !")
            }
        }
    }
});

</script>