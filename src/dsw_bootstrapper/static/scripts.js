$(function () {
    $.getJSON('/api/tenants', function (tenants) {
        const $sel = $('#tenant-select');
        $sel.empty();
        tenants.forEach(t => {
            $sel.append(`<option value="${t.uuid}">${t.name}</option>`);
        });
        if (tenants.length) {
            loadContents(tenants[0].uuid);
        }
    });


    $('#tenant-select').change(function () {
        loadContents($(this).val());
    });

    function loadPackages(data) {
        const $list = $('#packages-list');
        $list.empty();
        data.packages.forEach(p => {
            $list.append(`<li class="list-group-item"><label><input type="checkbox" value="${p.id}" class="form-check-input me-2"> ${p.name} (<code>${p.id}</code>)</label></li>`);
        });
        if (data.packages.length === 0) {
            $list.append('<li class="list-group-item">No packages available.</li>');
        }
    }

    function loadDocumentTemplates(data) {
        const $list = $('#document-templates-list');
        $list.empty();
        data.documentTemplates.forEach(dt => {
            $list.append(`<li class="list-group-item"><label><input type="checkbox" value="${dt.id}" class="form-check-input me-2"> ${dt.name} (<code>${dt.id}</code>)</label></li>`);
        });
        if (data.documentTemplates.length === 0) {
            $list.append('<li class="list-group-item">No document templates available.</li>');
        }
    }

    function loadQuestionnaires(data) {
        const $list = $('#questionnaires-list');
        $list.empty();
        data.questionnaires.forEach(q => {
            $list.append(`<li class="list-group-item"><label><input type="checkbox" value="${q.uuid}" class="form-check-input me-2"> ${q.name} (<code>${q.uuid}</code>, KM: <code>${q.packageId}</code>)</label></li>`);
        });
        if (data.questionnaires.length === 0) {
            $list.append('<li class="list-group-item">No projects available.</li>');
        }
    }

    function loadDocuments(data) {
        const $list = jQuery('#documents-list');
        $list.empty();
        data.documents.forEach(d => {
            $list.append(`<li class="list-group-item"><label><input type="checkbox" value="${d.uuid}" class="form-check-input me-2"> ${d.name} (<code>${d.uuid}</code>, DT: <code>${d.documentTemplateId}</code>)</label></li>`);
        });
        if (data.documents.length === 0) {
            $list.append('<li class="list-group-item">No documents available.</li>');
        }
    }

    function loadContents(uuid) {
        $.getJSON(`/api/tenants/${uuid}/contents`, function (data) {
            loadPackages(data);
            loadDocumentTemplates(data);
            loadQuestionnaires(data);
            loadDocuments(data);
        });
    }

    $('#build-btn').click(function () {
        const tenantUuid = $('#tenant-select').val();
        const packages = [];
        $('#packages-list input:checked').each(function () {
            packages.push({
                id: $(this).val(),
                includeDependencies: true
            })
        });
        const documentTemplates = [];
        $('#document-templates-list input:checked').each(function () {
            documentTemplates.push({
                id: $(this).val(),
            });
        });
        const questionnaires = [];
        $('#questionnaires-list input:checked').each(function () {
            questionnaires.push({
                uuid: $(this).val(),
                newUuid: true,
                anonymize: true,
                includeDependencies: true,
                includeVersions: true,
            });
        });
        const documents = [];
        $('#documents-list input:checked').each(function () {
            documents.push({
                uuid: $(this).val(),
                newUuid: true,
                anonymize: true,
                includeDependencies: true,
            });
        });
        const body = {
            name: $('#recipe-name').val() || 'Unnamed Recipe',
            description: $('#recipe-desc').val(),
            tenantUuid: tenantUuid,
            packages: packages,
            documentTemplates: documentTemplates,
            questionnaires: questionnaires,
            documents: documents,
        };
        $.ajax({
            url: '/api/recipe',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(body),
            xhrFields: {responseType: 'blob'},
            success: function (blob) {
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = 'seed-recipe.zip';
                link.click();
                $('#result').html('<div class="alert alert-success">Recipe built and downloaded.</div>');
            },
            error: function () {
                $('#result').html('<div class="alert alert-danger">Failed to build recipe.</div>');
            }
        });
    });
});