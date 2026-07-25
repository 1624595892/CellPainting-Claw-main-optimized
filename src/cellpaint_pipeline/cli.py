from __future__ import annotations

import argparse
import json
from importlib import import_module
from pathlib import Path

from cellpaint_pipeline.config import ProjectConfig


class _LazyCallable:
    def __init__(self, module_name: str, attr_name: str) -> None:
        self.module_name = module_name
        self.attr_name = attr_name

    def _resolve(self):
        module = import_module(self.module_name)
        return getattr(module, self.attr_name)

    def __call__(self, *args, **kwargs):
        return self._resolve()(*args, **kwargs)

    def __getattr__(self, name: str):
        return getattr(self._resolve(), name)


def _lazy(module_name: str, attr_name: str) -> _LazyCallable:
    return _LazyCallable(module_name, attr_name)


export_deepprofiler_input = _lazy('cellpaint_pipeline.adapters.deepprofiler', 'export_deepprofiler_input')
infer_deepprofiler_sources_from_workflow_root = _lazy('cellpaint_pipeline.adapters.deepprofiler', 'infer_deepprofiler_sources_from_workflow_root')
collect_deepprofiler_features = _lazy('cellpaint_pipeline.adapters.deepprofiler_features', 'collect_deepprofiler_features')
build_deepprofiler_project = _lazy('cellpaint_pipeline.adapters.deepprofiler_project', 'build_deepprofiler_project')
run_deepprofiler_profile = _lazy('cellpaint_pipeline.adapters.deepprofiler_project', 'run_deepprofiler_profile')
available_cppipe_templates = _lazy('cellpaint_pipeline.cppipe', 'available_cppipe_templates')
cppipe_template_definition_to_dict = _lazy('cellpaint_pipeline.cppipe', 'cppipe_template_definition_to_dict')
cppipe_validation_result_to_dict = _lazy('cellpaint_pipeline.cppipe', 'cppipe_validation_result_to_dict')
get_cppipe_template = _lazy('cellpaint_pipeline.cppipe', 'get_cppipe_template')
resolve_cppipe_selection = _lazy('cellpaint_pipeline.cppipe', 'resolve_cppipe_selection')
resolved_cppipe_selection_to_dict = _lazy('cellpaint_pipeline.cppipe', 'resolved_cppipe_selection_to_dict')
validate_cppipe_configuration = _lazy('cellpaint_pipeline.cppipe', 'validate_cppipe_configuration')
deepprofiler_pipeline_result_to_dict = _lazy('cellpaint_pipeline.deepprofiler_pipeline', 'deepprofiler_pipeline_result_to_dict')
run_deepprofiler_pipeline = _lazy('cellpaint_pipeline.deepprofiler_pipeline', 'run_deepprofiler_pipeline')
browse_quilt_package = _lazy('cellpaint_pipeline.data_access', 'browse_quilt_package')
build_data_access_status = _lazy('cellpaint_pipeline.data_access', 'build_data_access_status')
build_data_request = _lazy('cellpaint_pipeline.data_access', 'build_data_request')
build_download_plan = _lazy('cellpaint_pipeline.data_access', 'build_download_plan')
cache_gallery_listing = _lazy('cellpaint_pipeline.data_access', 'cache_gallery_listing')
cpgdata_prefix_list_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'cpgdata_prefix_list_result_to_dict')
cpgdata_sync_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'cpgdata_sync_result_to_dict')
data_access_status_to_dict = _lazy('cellpaint_pipeline.data_access', 'data_access_status_to_dict')
data_access_summary_to_dict = _lazy('cellpaint_pipeline.data_access', 'data_access_summary_to_dict')
data_download_execution_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'data_download_execution_result_to_dict')
data_download_plan_to_dict = _lazy('cellpaint_pipeline.data_access', 'data_download_plan_to_dict')
download_gallery_prefix = _lazy('cellpaint_pipeline.data_access', 'download_gallery_prefix')
download_gallery_source = _lazy('cellpaint_pipeline.data_access', 'download_gallery_source')
gallery_cache_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'gallery_cache_result_to_dict')
gallery_catalog_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'gallery_catalog_result_to_dict')
gallery_download_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'gallery_download_result_to_dict')
gallery_list_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'gallery_list_result_to_dict')
list_cpgdata_prefixes = _lazy('cellpaint_pipeline.data_access', 'list_cpgdata_prefixes')
load_download_plan = _lazy('cellpaint_pipeline.data_access', 'load_download_plan')
list_gallery_datasets = _lazy('cellpaint_pipeline.data_access', 'list_gallery_datasets')
list_gallery_prefixes = _lazy('cellpaint_pipeline.data_access', 'list_gallery_prefixes')
list_gallery_sources = _lazy('cellpaint_pipeline.data_access', 'list_gallery_sources')
list_quilt_packages = _lazy('cellpaint_pipeline.data_access', 'list_quilt_packages')
quilt_package_browse_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'quilt_package_browse_result_to_dict')
quilt_package_list_result_to_dict = _lazy('cellpaint_pipeline.data_access', 'quilt_package_list_result_to_dict')
summarize_data_access = _lazy('cellpaint_pipeline.data_access', 'summarize_data_access')
sync_cpgdata_index = _lazy('cellpaint_pipeline.data_access', 'sync_cpgdata_index')
sync_cpgdata_inventory = _lazy('cellpaint_pipeline.data_access', 'sync_cpgdata_inventory')
execute_download_plan = _lazy('cellpaint_pipeline.data_access', 'execute_download_plan')
write_download_plan = _lazy('cellpaint_pipeline.data_access', 'write_download_plan')
available_profiling_suites = _lazy('cellpaint_pipeline.delivery', 'available_profiling_suites')
available_segmentation_suites = _lazy('cellpaint_pipeline.delivery', 'available_segmentation_suites')
run_deepprofiler_full_stack = _lazy('cellpaint_pipeline.delivery', 'run_deepprofiler_full_stack')
run_full_pipeline = _lazy('cellpaint_pipeline.delivery', 'run_full_pipeline')
run_profiling_suite = _lazy('cellpaint_pipeline.delivery', 'run_profiling_suite')
run_segmentation_bundle = _lazy('cellpaint_pipeline.delivery', 'run_segmentation_bundle')
run_segmentation_suite = _lazy('cellpaint_pipeline.delivery', 'run_segmentation_suite')
run_smoke_test = _lazy('cellpaint_pipeline.delivery', 'run_smoke_test')
run_native_evaluation = _lazy('cellpaint_pipeline.evaluation', 'run_native_evaluation')
available_deepprofiler_modes = _lazy('cellpaint_pipeline.orchestration', 'available_deepprofiler_modes')
end_to_end_pipeline_result_to_dict = _lazy('cellpaint_pipeline.orchestration', 'end_to_end_pipeline_result_to_dict')
run_end_to_end_pipeline = _lazy('cellpaint_pipeline.orchestration', 'run_end_to_end_pipeline')
available_mcp_tools = _lazy('cellpaint_pipeline.mcp_tools', 'available_mcp_tools')
mcp_tool_catalog = _lazy('cellpaint_pipeline.mcp_tools', 'mcp_tool_catalog')
run_mcp_tool_to_dict = _lazy('cellpaint_pipeline.mcp_tools', 'run_mcp_tool_to_dict')
run_mcp_server = _lazy('cellpaint_pipeline.mcp_server', 'run_mcp_server')
available_public_api_entrypoints = _lazy('cellpaint_pipeline.public_api', 'available_public_api_entrypoints')
get_public_api_entrypoint = _lazy('cellpaint_pipeline.public_api', 'get_public_api_entrypoint')
public_api_contract_summary = _lazy('cellpaint_pipeline.public_api', 'public_api_contract_summary')
public_api_entrypoint_to_dict = _lazy('cellpaint_pipeline.public_api', 'public_api_entrypoint_to_dict')
run_public_api_entrypoint_to_dict = _lazy('cellpaint_pipeline.public_api', 'run_public_api_entrypoint_to_dict')
available_pipeline_presets = _lazy('cellpaint_pipeline.presets', 'available_pipeline_presets')
get_pipeline_preset_definition = _lazy('cellpaint_pipeline.presets', 'get_pipeline_preset_definition')
pipeline_preset_definition_to_dict = _lazy('cellpaint_pipeline.presets', 'pipeline_preset_definition_to_dict')
run_pipeline_preset = _lazy('cellpaint_pipeline.presets', 'run_pipeline_preset')
available_pipeline_skills = _lazy('cellpaint_pipeline.skills', 'available_pipeline_skills')
get_pipeline_skill_definition = _lazy('cellpaint_pipeline.skills', 'get_pipeline_skill_definition')
pipeline_skill_definition_to_dict = _lazy('cellpaint_pipeline.skills', 'pipeline_skill_definition_to_dict')
pipeline_skill_result_to_dict = _lazy('cellpaint_pipeline.skills', 'pipeline_skill_result_to_dict')
run_pipeline_skill = _lazy('cellpaint_pipeline.skills', 'run_pipeline_skill')
collect_validation_report = _lazy('cellpaint_pipeline.reporting', 'collect_validation_report')
segmentation_summary_to_dict = _lazy('cellpaint_pipeline.segmentation_native', 'segmentation_summary_to_dict')
summarize_segmentation_outputs = _lazy('cellpaint_pipeline.segmentation_native', 'summarize_segmentation_outputs')
write_segmentation_summary = _lazy('cellpaint_pipeline.segmentation_native', 'write_segmentation_summary')
available_workflows = _lazy('cellpaint_pipeline.workflows.orchestration', 'available_workflows')
run_workflow = _lazy('cellpaint_pipeline.workflows.orchestration', 'run_workflow')
available_profiling_scripts = _lazy('cellpaint_pipeline.workflows.profiling', 'available_profiling_scripts')
available_profiling_tasks = _lazy('cellpaint_pipeline.workflows.profiling', 'available_profiling_tasks')
run_profiling_native = _lazy('cellpaint_pipeline.workflows.profiling', 'run_profiling_native')
run_profiling_script = _lazy('cellpaint_pipeline.workflows.profiling', 'run_profiling_script')
run_profiling_task = _lazy('cellpaint_pipeline.workflows.profiling', 'run_profiling_task')
available_segmentation_scripts = _lazy('cellpaint_pipeline.workflows.segmentation', 'available_segmentation_scripts')
available_segmentation_tasks = _lazy('cellpaint_pipeline.workflows.segmentation', 'available_segmentation_tasks')
run_segmentation_native = _lazy('cellpaint_pipeline.workflows.segmentation', 'run_segmentation_native')
run_segmentation_script = _lazy('cellpaint_pipeline.workflows.segmentation', 'run_segmentation_script')
run_segmentation_task = _lazy('cellpaint_pipeline.workflows.segmentation', 'run_segmentation_task')


def build_parser(
    *,
    prog: str = 'cellpaint_pipeline',
    description: str = 'Standardized wrapper CLI for validated Cell Painting workflows.',
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    show_parser = subparsers.add_parser('show-config', help='Print the resolved project config.')
    show_parser.add_argument('--config', required=True, help='Path to project config JSON.')

    data_access_show_parser = subparsers.add_parser('show-data-access', help='Print the resolved data-access configuration.')
    data_access_show_parser.add_argument('--config', required=True, help='Path to project config JSON.')

    list_cppipe_templates_parser = subparsers.add_parser('list-cppipe-templates', help='List bundled .cppipe template keys exposed by the library.')
    list_cppipe_templates_parser.add_argument('--kind', choices=['profiling', 'segmentation'], default=None, help='Optionally limit the list to profiling or segmentation templates.')
    list_cppipe_templates_parser.add_argument('--config', default=None, help='Optional project config used to resolve bundled template paths.')

    describe_cppipe_template_parser = subparsers.add_parser('describe-cppipe-template', help='Describe one bundled .cppipe template and optionally resolve its path under a project config.')
    describe_cppipe_template_parser.add_argument('--template', required=True, help='Bundled .cppipe template key.')
    describe_cppipe_template_parser.add_argument('--config', default=None, help='Optional project config used to resolve the template path.')

    show_cppipe_selection_parser = subparsers.add_parser('show-cppipe-selection', help='Show the effective profiling or segmentation .cppipe selection under a project config.')
    show_cppipe_selection_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    show_cppipe_selection_parser.add_argument('--kind', choices=['profiling', 'segmentation', 'all'], default='all', help='Show one side or both effective selections.')

    validate_cppipe_config_parser = subparsers.add_parser('validate-cppipe-config', help='Validate the configured .cppipe template and custom-path selection.')
    validate_cppipe_config_parser.add_argument('--config', required=True, help='Path to project config JSON.')

    data_access_check_parser = subparsers.add_parser('check-data-access', help='Report data-access package and executable availability.')
    data_access_check_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    data_access_check_parser.add_argument('--strict', action='store_true', help='Return a non-zero exit code if required data-access packages are missing.')

    summarize_data_access_parser = subparsers.add_parser('summarize-data-access', help='Build a unified data-access summary across gallery, Quilt, and cpgdata adapters.')
    summarize_data_access_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    summarize_data_access_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override for gallery source listing.')
    summarize_data_access_parser.add_argument('--gallery-bucket', default=None, help='Optional gallery bucket override. Defaults to the configured gallery bucket.')
    summarize_data_access_parser.add_argument('--gallery-max-keys', type=int, default=1000, help='Maximum number of prefixes returned for gallery dataset/source listing calls.')
    summarize_data_access_parser.add_argument('--registry', default=None, help='Optional Quilt registry override. Defaults to data_access.quilt_registry.')
    summarize_data_access_parser.add_argument('--quilt-limit', type=int, default=None, help='Optional maximum number of Quilt packages to return.')
    summarize_data_access_parser.add_argument('--cpgdata-bucket', default=None, help='Optional cpgdata inventory bucket override. Defaults to data_access.cpgdata_inventory_bucket.')
    summarize_data_access_parser.add_argument('--cpgdata-prefix', default=None, help='Optional cpgdata prefix override. Defaults to data_access.cpgdata_inventory_prefix.')
    summarize_data_access_parser.add_argument('--cpgdata-recursive', action='store_true', help='Recursively list cpgdata prefix entries.')
    summarize_data_access_parser.add_argument('--cpgdata-limit', type=int, default=None, help='Optional maximum number of cpgdata entries to return.')
    summarize_data_access_parser.add_argument('--skip-gallery', action='store_true', help='Skip gallery dataset/source discovery in the combined summary.')
    summarize_data_access_parser.add_argument('--skip-quilt', action='store_true', help='Skip Quilt package discovery in the combined summary.')
    summarize_data_access_parser.add_argument('--skip-cpgdata', action='store_true', help='Skip cpgdata prefix discovery in the combined summary.')

    plan_data_access_parser = subparsers.add_parser('plan-data-access', help='Build a reusable download plan for gallery-backed data requests.')
    plan_data_access_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    plan_data_access_parser.add_argument('--mode', default='gallery-source', choices=['gallery-source', 'gallery-prefix'], help='Plan a source-based or raw-prefix gallery download.')
    plan_data_access_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override for gallery-source mode.')
    plan_data_access_parser.add_argument('--source-id', default=None, help='Optional source id override for gallery-source mode.')
    plan_data_access_parser.add_argument('--prefix', default=None, help='Required for gallery-prefix mode.')
    plan_data_access_parser.add_argument('--subprefix', default='', help='Optional nested prefix under a dataset/source root for gallery-source mode.')
    plan_data_access_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')
    plan_data_access_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    plan_data_access_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    plan_data_access_parser.add_argument('--max-files', type=int, default=None, help='Optional maximum number of matched objects to process.')
    plan_data_access_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files instead of skipping them during execution.')
    plan_data_access_parser.add_argument('--dry-run', action='store_true', help='Plan for dry-run execution.')
    plan_data_access_parser.add_argument('--output-dir', default=None, help='Optional local output directory override for the planned download.')
    plan_data_access_parser.add_argument('--manifest-path', default=None, help='Optional manifest path override for the planned download.')
    plan_data_access_parser.add_argument('--summary-max-keys', type=int, default=1000, help='Maximum number of gallery prefixes to inspect during summary-based validation.')
    plan_data_access_parser.add_argument('--skip-summary-check', action='store_true', help='Skip gallery summary validation while building the plan.')
    plan_data_access_parser.add_argument('--output-path', default=None, help='Optional JSON output path for persisting the planned download.')

    execute_download_plan_parser = subparsers.add_parser('execute-download-plan', help='Execute a previously generated download plan JSON file.')
    execute_download_plan_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    execute_download_plan_parser.add_argument('--plan-path', required=True, help='Path to a JSON file produced by plan-data-access.')

    list_gallery_parser = subparsers.add_parser('list-gallery-prefixes', help='List prefixes and objects from the configured Cell Painting Gallery bucket.')
    list_gallery_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    list_gallery_parser.add_argument('--prefix', default='', help='Optional S3 prefix to inspect.')
    list_gallery_parser.add_argument('--delimiter', default='/', help='Delimiter passed to list_objects_v2. Use an empty string for flat object listing.')
    list_gallery_parser.add_argument('--max-keys', type=int, default=1000, help='Maximum number of keys returned by the S3 listing request.')
    list_gallery_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')

    list_gallery_datasets_parser = subparsers.add_parser('list-gallery-datasets', help='List dataset-level prefixes from the configured Cell Painting Gallery bucket.')
    list_gallery_datasets_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    list_gallery_datasets_parser.add_argument('--max-keys', type=int, default=1000, help='Maximum number of dataset prefixes returned by the S3 listing request.')
    list_gallery_datasets_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')

    list_gallery_sources_parser = subparsers.add_parser('list-gallery-sources', help='List source-level prefixes for a dataset in the configured Cell Painting Gallery bucket.')
    list_gallery_sources_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    list_gallery_sources_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override. Defaults to data_access.default_dataset_id.')
    list_gallery_sources_parser.add_argument('--max-keys', type=int, default=1000, help='Maximum number of source prefixes returned by the S3 listing request.')
    list_gallery_sources_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')

    cache_gallery_parser = subparsers.add_parser('cache-gallery-prefixes', help='Write a JSON cache snapshot for a Cell Painting Gallery prefix listing.')
    cache_gallery_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    cache_gallery_parser.add_argument('--prefix', default='', help='Optional S3 prefix to inspect before caching.')
    cache_gallery_parser.add_argument('--delimiter', default='/', help='Delimiter passed to list_objects_v2. Use an empty string for flat object listing.')
    cache_gallery_parser.add_argument('--max-keys', type=int, default=1000, help='Maximum number of keys returned by the S3 listing request.')
    cache_gallery_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')
    cache_gallery_parser.add_argument('--output-path', default=None, help='Optional JSON output path. Defaults to data_access.index_cache_root.')

    download_gallery_prefix_parser = subparsers.add_parser('download-gallery-prefix', help='Download objects under a Cell Painting Gallery prefix into the local data cache.')
    download_gallery_prefix_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    download_gallery_prefix_parser.add_argument('--prefix', required=True, help='S3 prefix to download recursively.')
    download_gallery_prefix_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')
    download_gallery_prefix_parser.add_argument('--output-dir', default=None, help='Optional local output directory. Defaults to data_access.data_cache_root.')
    download_gallery_prefix_parser.add_argument('--manifest-path', default=None, help='Optional JSON manifest path. Defaults to download_manifest.json under the output directory.')
    download_gallery_prefix_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    download_gallery_prefix_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    download_gallery_prefix_parser.add_argument('--max-files', type=int, default=None, help='Optional maximum number of matched objects to process.')
    download_gallery_prefix_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files instead of skipping them.')
    download_gallery_prefix_parser.add_argument('--dry-run', action='store_true', help='Resolve matches and write the manifest without downloading files.')

    download_gallery_source_parser = subparsers.add_parser('download-gallery-source', help='Download objects for a dataset/source pair from the Cell Painting Gallery into the local data cache.')
    download_gallery_source_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    download_gallery_source_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override. Defaults to data_access.default_dataset_id.')
    download_gallery_source_parser.add_argument('--source-id', default=None, help='Optional source id override. Defaults to data_access.default_source_id.')
    download_gallery_source_parser.add_argument('--subprefix', default='', help='Optional nested prefix under the dataset/source root, for example images or workspace.')
    download_gallery_source_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to the configured gallery bucket.')
    download_gallery_source_parser.add_argument('--output-dir', default=None, help='Optional local output directory. Defaults to data_access.data_cache_root.')
    download_gallery_source_parser.add_argument('--manifest-path', default=None, help='Optional JSON manifest path. Defaults to download_manifest.json under the output directory.')
    download_gallery_source_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    download_gallery_source_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    download_gallery_source_parser.add_argument('--max-files', type=int, default=None, help='Optional maximum number of matched objects to process.')
    download_gallery_source_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files instead of skipping them.')
    download_gallery_source_parser.add_argument('--dry-run', action='store_true', help='Resolve matches and write the manifest without downloading files.')

    list_quilt_packages_parser = subparsers.add_parser('list-quilt-packages', help='List package names from the configured Quilt registry.')
    list_quilt_packages_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    list_quilt_packages_parser.add_argument('--registry', default=None, help='Optional Quilt registry override. Defaults to data_access.quilt_registry.')
    list_quilt_packages_parser.add_argument('--limit', type=int, default=None, help='Optional maximum number of package names to return.')

    browse_quilt_package_parser = subparsers.add_parser('browse-quilt-package', help='Browse one Quilt package and return its top-level keys.')
    browse_quilt_package_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    browse_quilt_package_parser.add_argument('--package-name', required=True, help='Quilt package name to browse.')
    browse_quilt_package_parser.add_argument('--registry', default=None, help='Optional Quilt registry override. Defaults to data_access.quilt_registry.')
    browse_quilt_package_parser.add_argument('--top-hash', default=None, help='Optional Quilt top hash override.')
    browse_quilt_package_parser.add_argument('--max-keys', type=int, default=200, help='Optional maximum number of top-level keys to return.')

    list_cpgdata_prefixes_parser = subparsers.add_parser('list-cpgdata-prefixes', help='List inventory/index-style prefixes using cpgdata utilities and AWS CLI.')
    list_cpgdata_prefixes_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    list_cpgdata_prefixes_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to data_access.cpgdata_inventory_bucket.')
    list_cpgdata_prefixes_parser.add_argument('--prefix', default=None, help='Optional prefix override. Defaults to data_access.cpgdata_inventory_prefix.')
    list_cpgdata_prefixes_parser.add_argument('--recursive', action='store_true', help='Recursively list matching entries.')
    list_cpgdata_prefixes_parser.add_argument('--limit', type=int, default=None, help='Optional maximum number of entries to return.')

    sync_cpgdata_index_parser = subparsers.add_parser('sync-cpgdata-index', help='Sync cpgdata index files from the inventory bucket into the local cache.')
    sync_cpgdata_index_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    sync_cpgdata_index_parser.add_argument('--output-dir', default=None, help='Optional local output directory. Defaults to data_access.index_cache_root/cpgdata_index.')
    sync_cpgdata_index_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to data_access.cpgdata_inventory_bucket.')
    sync_cpgdata_index_parser.add_argument('--prefix', default=None, help='Optional prefix override. Defaults to data_access.cpgdata_index_prefix.')
    sync_cpgdata_index_parser.add_argument('--include', default=None, help='Optional include glob passed to cpgdata sync_s3_prefix.')
    sync_cpgdata_index_parser.add_argument('--exclude', default=None, help='Optional exclude glob passed to cpgdata sync_s3_prefix.')
    sync_cpgdata_index_parser.add_argument('--show-progress', action='store_true', help='Show AWS CLI progress instead of using no-progress mode.')

    sync_cpgdata_inventory_parser = subparsers.add_parser('sync-cpgdata-inventory', help='Sync cpgdata inventory revision files into the local cache.')
    sync_cpgdata_inventory_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    sync_cpgdata_inventory_parser.add_argument('--output-dir', default=None, help='Optional local output directory. Defaults to data_access.index_cache_root/cpgdata_inventory.')
    sync_cpgdata_inventory_parser.add_argument('--bucket', default=None, help='Optional bucket override. Defaults to data_access.cpgdata_inventory_bucket.')
    sync_cpgdata_inventory_parser.add_argument('--prefix', default=None, help='Optional prefix override. Defaults to data_access.cpgdata_inventory_prefix.')
    sync_cpgdata_inventory_parser.add_argument('--revision', type=int, default=0, help='Inventory revision offset. 0 means latest revision.')

    profiling_parser = subparsers.add_parser('run-profiling', help='Run a profiling step.')
    profiling_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    profiling_parser.add_argument(
        '--script-key',
        default='full-pipeline',
        choices=available_profiling_scripts(),
        help='Profiling step alias.',
    )
    profiling_parser.add_argument(
        '--backend',
        default='script',
        choices=['script', 'native'],
        help='Use the validated backend script or a native in-library implementation when available.',
    )
    profiling_parser.add_argument('--output-path', default=None, help='Optional output path for native profiling outputs.')
    profiling_parser.add_argument('--output-dir', default=None, help='Optional output directory for native profiling steps that emit multiple files.')
    profiling_parser.add_argument('--manifest-path', default=None, help='Optional manifest path for native input validation.')
    profiling_parser.add_argument('--image-table-path', default=None, help='Optional image table path for native single-cell export.')
    profiling_parser.add_argument('--object-table-path', default=None, help='Optional object table path for native single-cell export.')
    profiling_parser.add_argument('--object-table', default=None, choices=['Cells', 'Cytoplasm', 'Nuclei'], help='Object table for native single-cell export.')
    profiling_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the backend script.')

    profiling_task_parser = subparsers.add_parser('run-profiling-task', help='Run a packaged profiling task.')
    profiling_task_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    profiling_task_parser.add_argument(
        '--task',
        default='full-post-mvp',
        choices=available_profiling_tasks(),
        help='Task-level profiling alias.',
    )
    profiling_task_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the backend script.')

    profiling_suite_parser = subparsers.add_parser('run-profiling-suite', help='Run a packaged profiling delivery suite.')
    profiling_suite_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    profiling_suite_parser.add_argument(
        '--suite',
        default='native',
        choices=available_profiling_suites(),
        help='High-level profiling suite alias.',
    )
    profiling_suite_parser.add_argument('--output-dir', default=None, help='Optional output directory for the profiling suite.')
    profiling_suite_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the underlying workflow backend when supported.')

    evaluation_parser = subparsers.add_parser('run-evaluation', help='Run the evaluation step.')
    evaluation_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    evaluation_parser.add_argument(
        '--backend',
        default='native',
        choices=['native', 'script'],
        help='Use the native in-library implementation or fall back to the validated backend script.',
    )
    evaluation_parser.add_argument('--output-dir', default=None, help='Optional output directory for native evaluation.')
    evaluation_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the script backend.')

    segmentation_parser = subparsers.add_parser('run-segmentation', help='Run a segmentation step.')
    segmentation_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    segmentation_parser.add_argument(
        '--script-key',
        default='full-segmentation',
        choices=available_segmentation_scripts(),
        help='Segmentation step alias.',
    )
    segmentation_parser.add_argument(
        '--backend',
        default='script',
        choices=['script', 'native'],
        help='Use the validated backend script or a native in-library implementation when available.',
    )
    segmentation_parser.add_argument('--output-path', default=None, help='Optional output path for native segmentation outputs.')
    segmentation_parser.add_argument('--manifest-path', default=None, help='Optional manifest path override for native single-cell preview generation.')
    segmentation_parser.add_argument('--mode', default='masked', choices=['masked', 'unmasked'], help='Crop mode for segmentation preview steps.')
    segmentation_parser.add_argument('--workers', type=int, default=0, help='Worker count for segmentation steps that support parallel execution.')
    segmentation_parser.add_argument('--chunk-size', type=int, default=64, help='Chunk size for native/script single-cell PNG preview generation.')
    segmentation_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing preview outputs for native/sample-preview execution.')
    segmentation_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the backend script.')

    segmentation_task_parser = subparsers.add_parser('run-segmentation-task', help='Run a packaged segmentation task.')
    segmentation_task_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    segmentation_task_parser.add_argument(
        '--task',
        default='full-post-mvp-segmentation',
        choices=available_segmentation_tasks(),
        help='Task-level segmentation alias.',
    )
    segmentation_task_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the backend script.')

    segmentation_suite_parser = subparsers.add_parser('run-segmentation-suite', help='Run a packaged segmentation delivery suite.')
    segmentation_suite_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    segmentation_suite_parser.add_argument(
        '--suite',
        default='mask-export',
        choices=available_segmentation_suites(),
        help='High-level segmentation suite alias.',
    )
    segmentation_suite_parser.add_argument('--output-dir', default=None, help='Optional output directory for the segmentation suite.')
    segmentation_suite_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the underlying workflow backend when supported.')

    segmentation_bundle_parser = subparsers.add_parser('run-segmentation-bundle', help='Run the default high-level segmentation bundle.')
    segmentation_bundle_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    segmentation_bundle_parser.add_argument('--output-dir', default=None, help='Optional output directory for the segmentation bundle.')
    segmentation_bundle_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the underlying workflow backend when supported.')

    deepprofiler_full_stack_parser = subparsers.add_parser('run-deepprofiler-full-stack', help='Run the default DeepProfiler full-stack segmentation bundle.')
    deepprofiler_full_stack_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    deepprofiler_full_stack_parser.add_argument('--output-dir', default=None, help='Optional output directory for the DeepProfiler full-stack bundle.')
    deepprofiler_full_stack_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the underlying workflow backend when supported.')

    full_pipeline_parser = subparsers.add_parser('run-full-pipeline', help='Run the packaged profiling and segmentation suites together.')
    full_pipeline_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    full_pipeline_parser.add_argument(
        '--profiling-suite',
        default='native',
        choices=available_profiling_suites(),
        help='Profiling suite alias used by the full pipeline.',
    )
    full_pipeline_parser.add_argument(
        '--segmentation-suite',
        default='mask-export',
        choices=available_segmentation_suites(),
        help='Segmentation suite alias used by the full pipeline.',
    )
    full_pipeline_parser.add_argument('--output-dir', default=None, help='Optional output directory for the full pipeline delivery.')
    full_pipeline_parser.add_argument('--skip-validation-report', action='store_true', help='Skip writing a delivery-local validation report snapshot.')

    orchestrated_pipeline_parser = subparsers.add_parser('run-end-to-end-pipeline', help='Run the top-level orchestration entrypoint across data access, profiling, segmentation, and optional DeepProfiler.')
    orchestrated_pipeline_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    orchestrated_pipeline_parser.add_argument('--output-dir', default=None, help='Optional output directory for the orchestrated pipeline run.')
    orchestrated_pipeline_parser.add_argument('--profiling-suite', default='native', choices=available_profiling_suites(), help='Profiling suite alias used when profiling is enabled.')
    orchestrated_pipeline_parser.add_argument('--segmentation-suite', default='mask-export', choices=available_segmentation_suites(), help='Segmentation suite alias used when DeepProfiler mode is off.')
    orchestrated_pipeline_parser.add_argument('--deepprofiler-mode', default='off', choices=available_deepprofiler_modes(), help='Force the segmentation branch into DeepProfiler export or full-stack mode.')
    orchestrated_pipeline_parser.add_argument('--skip-profiling', action='store_true', help='Skip the profiling stage.')
    orchestrated_pipeline_parser.add_argument('--skip-segmentation', action='store_true', help='Skip the segmentation stage.')
    orchestrated_pipeline_parser.add_argument('--skip-validation-report', action='store_true', help='Skip writing a validation report snapshot.')
    orchestrated_pipeline_parser.add_argument('--include-data-access-summary', action='store_true', help='Write a combined data-access summary snapshot into the orchestration output.')
    orchestrated_pipeline_parser.add_argument('--plan-data-download', action='store_true', help='Build and persist a gallery download plan before workflow execution.')
    orchestrated_pipeline_parser.add_argument('--execute-data-download-step', action='store_true', help='Execute the planned gallery download step as part of the orchestration run.')
    orchestrated_pipeline_parser.add_argument('--request-mode', default='gallery-source', choices=['gallery-source', 'gallery-prefix'], help='How to interpret the optional data request inputs.')
    orchestrated_pipeline_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override for gallery-source requests.')
    orchestrated_pipeline_parser.add_argument('--source-id', default=None, help='Optional source id override for gallery-source requests.')
    orchestrated_pipeline_parser.add_argument('--prefix', default=None, help='Raw gallery prefix used by gallery-prefix requests.')
    orchestrated_pipeline_parser.add_argument('--subprefix', default='', help='Optional nested subprefix under a dataset/source root.')
    orchestrated_pipeline_parser.add_argument('--bucket', default=None, help='Optional bucket override for the data request.')
    orchestrated_pipeline_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    orchestrated_pipeline_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    orchestrated_pipeline_parser.add_argument('--max-files', type=int, default=None, help='Optional max file count for the data request.')
    orchestrated_pipeline_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files during download execution.')
    orchestrated_pipeline_parser.add_argument('--dry-run', action='store_true', help='Mark the embedded data request as dry-run.')
    orchestrated_pipeline_parser.add_argument('--plan-path', default=None, help='Optional path to a previously saved download plan JSON. If provided, request-building flags are ignored for execution.')
    orchestrated_pipeline_parser.add_argument('--data-summary-max-keys', type=int, default=1000, help='Maximum number of gallery prefixes inspected during summary-backed planning.')

    list_presets_parser = subparsers.add_parser('list-pipeline-presets', help='List the available high-level pipeline presets.')

    run_preset_parser = subparsers.add_parser('run-pipeline-preset', help='Run a named high-level pipeline preset.')
    run_preset_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    run_preset_parser.add_argument('--preset', required=True, choices=available_pipeline_presets(), help='Named pipeline preset.')
    run_preset_parser.add_argument('--output-dir', default=None, help='Optional output directory for the preset run.')
    run_preset_parser.add_argument('--plan-path', default=None, help='Optional path to a previously saved download plan JSON.')
    run_preset_parser.add_argument('--profiling-suite', default=None, choices=available_profiling_suites(), help='Optional profiling suite override.')
    run_preset_parser.add_argument('--segmentation-suite', default=None, choices=available_segmentation_suites(), help='Optional segmentation suite override.')
    run_preset_parser.add_argument('--deepprofiler-mode', default=None, choices=available_deepprofiler_modes(), help='Optional DeepProfiler mode override.')
    run_preset_parser.add_argument('--request-mode', default='gallery-source', choices=['gallery-source', 'gallery-prefix'], help='How to interpret optional request inputs when no plan-path is supplied.')
    run_preset_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override for gallery-source requests.')
    run_preset_parser.add_argument('--source-id', default=None, help='Optional source id override for gallery-source requests.')
    run_preset_parser.add_argument('--prefix', default=None, help='Raw gallery prefix used by gallery-prefix requests.')
    run_preset_parser.add_argument('--subprefix', default='', help='Optional nested subprefix under a dataset/source root.')
    run_preset_parser.add_argument('--bucket', default=None, help='Optional bucket override for the data request.')
    run_preset_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    run_preset_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    run_preset_parser.add_argument('--max-files', type=int, default=None, help='Optional max file count for the data request.')
    run_preset_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files during download execution.')
    run_preset_parser.add_argument('--dry-run', action='store_true', help='Mark the embedded data request as dry-run.')

    list_skills_parser = subparsers.add_parser('list-pipeline-skills', help='List the available task-oriented pipeline skills.')
    list_skills_parser.add_argument('--include-advanced', action='store_true', help='Also show advanced direct-control skill names.')
    list_skills_parser.add_argument('--include-legacy', action='store_true', help='Also show legacy compatibility skill names.')

    run_skill_parser = subparsers.add_parser('run-pipeline-skill', help='Run a named task-oriented pipeline skill.')
    run_skill_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    run_skill_parser.add_argument('--skill', required=True, help='Named pipeline skill.')
    run_skill_parser.add_argument('--output-dir', default=None, help='Optional output directory for the skill run.')
    run_skill_parser.add_argument('--plan-path', default=None, help='Optional path to a previously saved download plan JSON.')
    run_skill_parser.add_argument('--workflow-root', default=None, help='Optional workflow root used by segmentation or DeepProfiler bridge skills.')
    run_skill_parser.add_argument('--export-root', default=None, help='Optional DeepProfiler export root used by project-building skills.')
    run_skill_parser.add_argument('--project-root', default=None, help='Optional DeepProfiler project root used by profiling or feature-collection skills.')
    run_skill_parser.add_argument('--image-csv-path', default=None, help='Optional explicit Image.csv path.')
    run_skill_parser.add_argument('--nuclei-csv-path', default=None, help='Optional explicit Nuclei.csv path.')
    run_skill_parser.add_argument('--load-data-csv-path', default=None, help='Optional explicit load-data CSV path.')
    run_skill_parser.add_argument('--manifest-path', default=None, help='Optional explicit manifest CSV path for validation-like skills.')
    run_skill_parser.add_argument('--object-table-path', default=None, help='Optional explicit CellProfiler object table CSV path.')
    run_skill_parser.add_argument('--single-cell-path', default=None, help='Optional explicit single-cell table path for pycytominer skills.')
    run_skill_parser.add_argument('--aggregated-path', default=None, help='Optional explicit aggregated profile table path for pycytominer annotation or downstream stages.')
    run_skill_parser.add_argument('--annotated-path', default=None, help='Optional explicit annotated profile table path for pycytominer normalization or downstream stages.')
    run_skill_parser.add_argument('--normalized-path', default=None, help='Optional explicit normalized profile table path for pycytominer feature selection.')
    run_skill_parser.add_argument('--feature-selected-path', default=None, help='Optional explicit feature-selected profile table path for summarize-classical-profiles.')
    run_skill_parser.add_argument('--single-cell-parquet-path', default=None, help='Optional explicit DeepProfiler single-cell parquet path for summarize-deepprofiler-profiles.')
    run_skill_parser.add_argument('--well-aggregated-parquet-path', default=None, help='Optional explicit DeepProfiler well-level parquet path for summarize-deepprofiler-profiles.')
    run_skill_parser.add_argument('--object-table', default=None, help='Optional CellProfiler object table name override, for example Cells or Cytoplasm.')
    run_skill_parser.add_argument('--crop-mode', default=None, choices=['masked', 'unmasked'], help='Optional crop mode override for export-single-cell-crops.')
    run_skill_parser.add_argument('--workers', type=int, default=0, help='Optional worker override for crop-export skills.')
    run_skill_parser.add_argument('--chunk-size', type=int, default=64, help='Optional chunk size override for preview-like skills.')
    run_skill_parser.add_argument('--gpu', default=None, help='Optional GPU identifier override for DeepProfiler profile runs.')
    run_skill_parser.add_argument('--experiment-name', default=None, help='Optional DeepProfiler experiment name override.')
    run_skill_parser.add_argument('--config-filename', default=None, help='Optional DeepProfiler project config filename override.')
    run_skill_parser.add_argument('--metadata-filename', default=None, help='Optional DeepProfiler metadata filename override.')
    run_skill_parser.add_argument('--request-mode', default='gallery-source', choices=['gallery-source', 'gallery-prefix'], help='How to interpret optional request inputs when no plan-path is supplied.')
    run_skill_parser.add_argument('--dataset-id', default=None, help='Optional dataset id override for gallery-source requests.')
    run_skill_parser.add_argument('--source-id', default=None, help='Optional source id override for gallery-source requests.')
    run_skill_parser.add_argument('--prefix', default=None, help='Raw gallery prefix used by gallery-prefix requests.')
    run_skill_parser.add_argument('--subprefix', default='', help='Optional nested subprefix under a dataset/source root.')
    run_skill_parser.add_argument('--bucket', default=None, help='Optional bucket override for the data request.')
    run_skill_parser.add_argument('--include-substring', action='append', default=None, help='Only keep object keys containing this substring. May be repeated.')
    run_skill_parser.add_argument('--exclude-substring', action='append', default=None, help='Skip object keys containing this substring. May be repeated.')
    run_skill_parser.add_argument('--max-files', type=int, default=None, help='Optional max file count for the data request.')
    run_skill_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing local files during download execution.')
    run_skill_parser.add_argument('--dry-run', action='store_true', help='Mark the embedded data request as dry-run.')

    segmentation_summary_parser = subparsers.add_parser('summarize-segmentation', help='Summarize current segmentation artifacts.')
    segmentation_summary_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    segmentation_summary_parser.add_argument('--output-path', default=None, help='Optional JSON path to write the segmentation summary.')

    validation_report_parser = subparsers.add_parser('collect-validation-report', help='Collect known validation artifacts into one report.')
    validation_report_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    validation_report_parser.add_argument('--output-path', default=None, help='Optional JSON path for the aggregated validation report.')

    list_mcp_tools_parser = subparsers.add_parser('list-mcp-tools', help='List the MCP tool wrappers exposed by the library.')

    show_mcp_catalog_parser = subparsers.add_parser('show-mcp-tool-catalog', help='Print the MCP tool catalog with schemas and routing metadata.')

    run_mcp_tool_parser = subparsers.add_parser('run-mcp-tool', help='Run one MCP wrapper tool through a single dispatcher.')
    run_mcp_tool_parser.add_argument('--tool', required=True, choices=available_mcp_tools(), help='MCP tool name.')
    run_mcp_tool_parser.add_argument('--config', default=None, help='Optional project config JSON. Required for config-backed MCP tools.')
    run_mcp_tool_parser.add_argument('--params-json', default='{}', help='JSON object of keyword arguments passed to the selected MCP tool.')

    list_public_api_parser = subparsers.add_parser('list-public-api-entrypoints', help='List the recommended machine-readable public API entrypoints.')

    show_public_api_parser = subparsers.add_parser('show-public-api-contract', help='Print the grouped public API contract summary.')

    run_public_api_parser = subparsers.add_parser('run-public-api-entrypoint', help='Dispatch one public API entrypoint through a single automation-friendly wrapper.')
    run_public_api_parser.add_argument('--entrypoint', required=True, choices=available_public_api_entrypoints(), help='Public API entrypoint name.')
    run_public_api_parser.add_argument('--config', default=None, help='Optional project config JSON. Required for config-backed entrypoints.')
    run_public_api_parser.add_argument('--params-json', default='{}', help='JSON object of keyword arguments passed to the selected entrypoint.')

    serve_mcp_parser = subparsers.add_parser('serve-mcp', help='Run the optional MCP server wrapper for OpenClaw or other MCP clients.')
    serve_mcp_parser.add_argument('--transport', default='stdio', choices=['stdio', 'streamable-http'], help='MCP transport mode.')
    serve_mcp_parser.add_argument('--host', default=None, help='Optional host override for HTTP transport.')
    serve_mcp_parser.add_argument('--port', type=int, default=None, help='Optional port override for HTTP transport.')
    serve_mcp_parser.add_argument('--path', default=None, help='Optional HTTP mount path override for streamable-http transport.')

    smoke_test_parser = subparsers.add_parser('smoke-test', help='Run a lightweight delivery smoke test and write a JSON report.')
    smoke_test_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    smoke_test_parser.add_argument('--output-path', default=None, help='Optional JSON path for the smoke test report.')

    workflow_parser = subparsers.add_parser('run-workflow', help='Run a packaged multi-step workflow.')
    workflow_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    workflow_parser.add_argument(
        '--workflow',
        required=True,
        choices=available_workflows(),
        help='Workflow alias.',
    )
    workflow_parser.add_argument('--output-dir', default=None, help='Optional export directory for workflows that create exports.')
    workflow_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help='Extra args forwarded to the main backend step.')

    export_parser = subparsers.add_parser(
        'export-deepprofiler-input',
        help='Export field metadata and nuclei locations for DeepProfiler-style consumption.',
    )
    export_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    export_parser.add_argument('--output-dir', default=None, help='Optional export directory. Defaults to deepprofiler_export_root in config.')
    export_parser.add_argument('--workflow-root', default=None, help='Optional workflow root containing cellprofiler_masks and load_data_for_segmentation.csv.')
    export_parser.add_argument('--image-csv-path', default=None, help='Optional Image.csv override for DeepProfiler export.')
    export_parser.add_argument('--nuclei-csv-path', default=None, help='Optional Nuclei.csv override for DeepProfiler export.')
    export_parser.add_argument('--load-data-path', default=None, help='Optional segmentation load-data CSV override for DeepProfiler export.')
    export_parser.add_argument('--source-label', default=None, help='Optional free-text label recorded in the DeepProfiler export manifest.')

    project_parser = subparsers.add_parser(
        'build-deepprofiler-project',
        help='Materialize a DeepProfiler project directory from a prepared DeepProfiler export.',
    )
    project_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    project_parser.add_argument('--output-dir', default=None, help='Optional output directory for the DeepProfiler project.')
    project_parser.add_argument('--workflow-root', default=None, help='Optional workflow root containing deepprofiler_export/.')
    project_parser.add_argument('--export-root', default=None, help='Optional DeepProfiler export root override.')
    project_parser.add_argument('--experiment-name', default=None, help='Optional DeepProfiler experiment name override.')
    project_parser.add_argument('--config-name', default=None, help='Optional config filename under inputs/config/.')
    project_parser.add_argument('--metadata-name', default=None, help='Optional metadata filename under inputs/metadata/.')

    profile_parser = subparsers.add_parser(
        'run-deepprofiler-profile',
        help='Run the DeepProfiler profile command inside a prepared DeepProfiler project.',
    )
    profile_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    profile_parser.add_argument('--project-root', required=True, help='Path to the prepared DeepProfiler project root.')
    profile_parser.add_argument('--experiment-name', default=None, help='Optional DeepProfiler experiment name override.')
    profile_parser.add_argument('--config-name', default=None, help='Optional config filename override.')
    profile_parser.add_argument('--metadata-name', default=None, help='Optional metadata filename override.')
    profile_parser.add_argument('--gpu', default=None, help='Optional GPU id forwarded to DeepProfiler.')

    collect_parser = subparsers.add_parser(
        'collect-deepprofiler-features',
        help='Collect DeepProfiler .npz outputs into pycytominer-friendly single-cell and well-level tables.',
    )
    collect_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    collect_parser.add_argument('--project-root', required=True, help='Path to the prepared DeepProfiler project root.')
    collect_parser.add_argument('--output-dir', default=None, help='Optional output directory for collected DeepProfiler tables.')
    collect_parser.add_argument('--experiment-name', default=None, help='Optional DeepProfiler experiment name override.')

    pipeline_parser = subparsers.add_parser(
        'run-deepprofiler-pipeline',
        help='Run the full DeepProfiler export, project build, profile, and feature collection chain.',
    )
    pipeline_parser.add_argument('--config', required=True, help='Path to project config JSON.')
    pipeline_parser.add_argument('--output-dir', default=None, help='Optional output directory for the standardized DeepProfiler run root.')
    pipeline_parser.add_argument('--workflow-root', default=None, help='Optional workflow root used to infer Image.csv, Nuclei.csv, and load_data_for_segmentation.csv.')
    pipeline_parser.add_argument('--image-csv-path', default=None, help='Optional Image.csv override for DeepProfiler pipeline input.')
    pipeline_parser.add_argument('--nuclei-csv-path', default=None, help='Optional Nuclei.csv override for DeepProfiler pipeline input.')
    pipeline_parser.add_argument('--load-data-path', default=None, help='Optional segmentation load-data CSV override for DeepProfiler pipeline input.')
    pipeline_parser.add_argument('--source-label', default=None, help='Optional free-text label recorded in the DeepProfiler export manifest.')
    pipeline_parser.add_argument('--experiment-name', default=None, help='Optional DeepProfiler experiment name override.')
    pipeline_parser.add_argument('--config-name', default=None, help='Optional config filename under inputs/config/.')
    pipeline_parser.add_argument('--metadata-name', default=None, help='Optional metadata filename under inputs/metadata/.')
    pipeline_parser.add_argument('--gpu', default=None, help='Optional GPU id forwarded to DeepProfiler.')

    return parser


def _normalize_extra_args(extra_args: list[str]) -> list[str]:
    if extra_args and extra_args[0] == '--':
        return extra_args[1:]
    return extra_args


def main(
    argv: list[str] | None = None,
    *,
    prog: str = 'cellpaint_pipeline',
    description: str = 'Standardized wrapper CLI for validated Cell Painting workflows.',
) -> int:
    parser = build_parser(prog=prog, description=description)
    args = parser.parse_args(argv)

    try:
        if args.command == 'show-config':
            config = ProjectConfig.from_json(args.config)
            print(json.dumps(config.as_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'show-data-access':
            config = ProjectConfig.from_json(args.config)
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.data_access',
                'config': config.data_access.as_dict(),
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-cppipe-templates':
            config = ProjectConfig.from_json(args.config) if args.config else None
            payload = [
                cppipe_template_definition_to_dict(get_cppipe_template(key), config=config)
                for key in available_cppipe_templates(kind=args.kind)
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'describe-cppipe-template':
            config = ProjectConfig.from_json(args.config) if args.config else None
            payload = cppipe_template_definition_to_dict(get_cppipe_template(args.template), config=config)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'show-cppipe-selection':
            config = ProjectConfig.from_json(args.config)
            kinds = ['profiling', 'segmentation'] if args.kind == 'all' else [args.kind]
            payload = [
                resolved_cppipe_selection_to_dict(resolve_cppipe_selection(config, kind))
                for kind in kinds
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'validate-cppipe-config':
            config = ProjectConfig.from_json(args.config)
            result = validate_cppipe_configuration(config)
            print(json.dumps(cppipe_validation_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'check-data-access':
            config = ProjectConfig.from_json(args.config)
            status = build_data_access_status(config)
            print(json.dumps(data_access_status_to_dict(status), indent=2, ensure_ascii=False))
            return 0 if status.ok or not args.strict else 1

        if args.command == 'summarize-data-access':
            config = ProjectConfig.from_json(args.config)
            result = summarize_data_access(
                config,
                dataset_id=args.dataset_id,
                gallery_bucket=args.gallery_bucket,
                gallery_max_keys=args.gallery_max_keys,
                registry=args.registry,
                quilt_limit=args.quilt_limit,
                cpgdata_bucket=args.cpgdata_bucket,
                cpgdata_prefix=args.cpgdata_prefix,
                cpgdata_recursive=args.cpgdata_recursive,
                cpgdata_limit=args.cpgdata_limit,
                include_gallery=not args.skip_gallery,
                include_quilt=not args.skip_quilt,
                include_cpgdata=not args.skip_cpgdata,
            )
            print(json.dumps(data_access_summary_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'plan-data-access':
            config = ProjectConfig.from_json(args.config)
            request = build_data_request(
                mode=args.mode,
                dataset_id=args.dataset_id,
                source_id=args.source_id,
                prefix=args.prefix,
                subprefix=args.subprefix,
                bucket=args.bucket,
                include_substrings=args.include_substring or [],
                exclude_substrings=args.exclude_substring or [],
                max_files=args.max_files,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
            )
            plan = build_download_plan(
                config,
                request,
                summary_max_keys=args.summary_max_keys,
                validate_with_summary=not args.skip_summary_check,
            )
            payload = data_download_plan_to_dict(plan)
            if args.output_path:
                output_path = write_download_plan(plan, Path(args.output_path).expanduser().resolve())
                payload['plan_path'] = str(output_path)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0 if plan.ok else 1

        if args.command == 'execute-download-plan':
            config = ProjectConfig.from_json(args.config)
            plan = load_download_plan(Path(args.plan_path).expanduser().resolve())
            result = execute_download_plan(config, plan)
            print(json.dumps(data_download_execution_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'list-gallery-prefixes':
            config = ProjectConfig.from_json(args.config)
            result = list_gallery_prefixes(
                config,
                prefix=args.prefix,
                delimiter=args.delimiter,
                max_keys=args.max_keys,
                bucket=args.bucket,
            )
            print(json.dumps(gallery_list_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-gallery-datasets':
            config = ProjectConfig.from_json(args.config)
            result = list_gallery_datasets(
                config,
                max_keys=args.max_keys,
                bucket=args.bucket,
            )
            print(json.dumps(gallery_catalog_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-gallery-sources':
            config = ProjectConfig.from_json(args.config)
            result = list_gallery_sources(
                config,
                dataset_id=args.dataset_id,
                max_keys=args.max_keys,
                bucket=args.bucket,
            )
            print(json.dumps(gallery_catalog_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'cache-gallery-prefixes':
            config = ProjectConfig.from_json(args.config)
            result = cache_gallery_listing(
                config,
                prefix=args.prefix,
                delimiter=args.delimiter,
                max_keys=args.max_keys,
                bucket=args.bucket,
                output_path=Path(args.output_path).expanduser().resolve() if args.output_path else None,
            )
            print(json.dumps(gallery_cache_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'download-gallery-prefix':
            config = ProjectConfig.from_json(args.config)
            result = download_gallery_prefix(
                config,
                prefix=args.prefix,
                bucket=args.bucket,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
                include_substrings=args.include_substring or [],
                exclude_substrings=args.exclude_substring or [],
                max_files=args.max_files,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )
            print(json.dumps(gallery_download_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'download-gallery-source':
            config = ProjectConfig.from_json(args.config)
            result = download_gallery_source(
                config,
                dataset_id=args.dataset_id,
                source_id=args.source_id,
                subprefix=args.subprefix,
                bucket=args.bucket,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
                include_substrings=args.include_substring or [],
                exclude_substrings=args.exclude_substring or [],
                max_files=args.max_files,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )
            print(json.dumps(gallery_download_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-quilt-packages':
            config = ProjectConfig.from_json(args.config)
            result = list_quilt_packages(config, registry=args.registry, limit=args.limit)
            print(json.dumps(quilt_package_list_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'browse-quilt-package':
            config = ProjectConfig.from_json(args.config)
            result = browse_quilt_package(
                config,
                package_name=args.package_name,
                registry=args.registry,
                top_hash=args.top_hash,
                max_keys=args.max_keys,
            )
            print(json.dumps(quilt_package_browse_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-cpgdata-prefixes':
            config = ProjectConfig.from_json(args.config)
            result = list_cpgdata_prefixes(
                config,
                bucket=args.bucket,
                prefix=args.prefix,
                recursive=args.recursive,
                limit=args.limit,
            )
            print(json.dumps(cpgdata_prefix_list_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'sync-cpgdata-index':
            config = ProjectConfig.from_json(args.config)
            result = sync_cpgdata_index(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                bucket=args.bucket,
                prefix=args.prefix,
                include=args.include,
                exclude=args.exclude,
                no_progress=not args.show_progress,
            )
            print(json.dumps(cpgdata_sync_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'sync-cpgdata-inventory':
            config = ProjectConfig.from_json(args.config)
            result = sync_cpgdata_inventory(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                bucket=args.bucket,
                prefix=args.prefix,
                revision=args.revision,
            )
            print(json.dumps(cpgdata_sync_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-profiling':
            config = ProjectConfig.from_json(args.config)
            if args.backend == 'script':
                result = run_profiling_script(config, args.script_key, _normalize_extra_args(args.extra_args))
                print(f'[cellpaint_pipeline] completed: {result.label}')
                return result.returncode
            native_result = run_profiling_native(
                config,
                args.script_key,
                output_path=Path(args.output_path).expanduser().resolve() if args.output_path else None,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
                image_table_path=Path(args.image_table_path).expanduser().resolve() if args.image_table_path else None,
                object_table_path=Path(args.object_table_path).expanduser().resolve() if args.object_table_path else None,
                object_table=args.object_table,
            )
            print(json.dumps(_native_result_to_dict(native_result), indent=2, ensure_ascii=False))
            return 0 if _native_result_ok(native_result) else 1

        if args.command == 'run-profiling-task':
            config = ProjectConfig.from_json(args.config)
            result = run_profiling_task(config, args.task, _normalize_extra_args(args.extra_args))
            print(f'[cellpaint_pipeline] completed: {result.label}')
            return result.returncode

        if args.command == 'run-profiling-suite':
            config = ProjectConfig.from_json(args.config)
            result = run_profiling_suite(
                config,
                args.suite,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                extra_args=_normalize_extra_args(args.extra_args),
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.delivery',
                'suite_type': 'profiling',
                'suite_key': result.suite_key,
                'workflow_key': result.workflow_key,
                'output_dir': str(result.output_dir),
                'manifest_path': str(result.manifest_path) if result.manifest_path else None,
                'step_count': result.step_count,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-evaluation':
            config = ProjectConfig.from_json(args.config)
            if args.backend == 'script':
                result = run_profiling_script(config, 'evaluation', _normalize_extra_args(args.extra_args))
                print(f'[cellpaint_pipeline] completed: {result.label}')
                return result.returncode
            native_result = run_native_evaluation(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
            )
            print(json.dumps({
                'implementation': 'native',
                'output_dir': str(native_result.output_dir),
                'n_wells': native_result.n_wells,
                'n_feature_columns': native_result.n_feature_columns,
                'sample_id_column': native_result.sample_id_column,
                'run_manifest_path': str(native_result.run_manifest_path),
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-segmentation':
            config = ProjectConfig.from_json(args.config)
            if args.backend == 'script':
                extra_args = _normalize_extra_args(args.extra_args)
                if args.overwrite:
                    extra_args = ['--overwrite', *extra_args]
                if args.script_key in {'extract-single-cell-crops', 'generate-png-previews'}:
                    extra_args = ['--mode', args.mode, *extra_args]
                if args.script_key in {'extract-single-cell-crops', 'generate-png-previews'} and args.workers > 0:
                    extra_args = ['--workers', str(args.workers), *extra_args]
                if args.script_key == 'generate-png-previews' and args.chunk_size > 0:
                    extra_args = ['--chunk-size', str(args.chunk_size), *extra_args]
                result = run_segmentation_script(config, args.script_key, extra_args)
                print(f'[cellpaint_pipeline] completed: {result.label}')
                return result.returncode
            native_result = run_segmentation_native(
                config,
                args.script_key,
                output_path=Path(args.output_path).expanduser().resolve() if args.output_path else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
                mode=args.mode,
                workers=args.workers,
                chunk_size=args.chunk_size,
                overwrite=args.overwrite,
            )
            print(json.dumps(_native_segmentation_result_to_dict(native_result), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-segmentation-task':
            config = ProjectConfig.from_json(args.config)
            result = run_segmentation_task(config, args.task, _normalize_extra_args(args.extra_args))
            print(f'[cellpaint_pipeline] completed: {result.label}')
            return result.returncode

        if args.command == 'run-segmentation-suite':
            config = ProjectConfig.from_json(args.config)
            result = run_segmentation_suite(
                config,
                args.suite,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                extra_args=_normalize_extra_args(args.extra_args),
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.delivery',
                'suite_type': 'segmentation',
                'suite_key': result.suite_key,
                'workflow_key': result.workflow_key,
                'output_dir': str(result.output_dir),
                'manifest_path': str(result.manifest_path) if result.manifest_path else None,
                'step_count': result.step_count,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-segmentation-bundle':
            config = ProjectConfig.from_json(args.config)
            result = run_segmentation_bundle(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                extra_args=_normalize_extra_args(args.extra_args),
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.delivery',
                'suite_type': 'segmentation',
                'suite_key': result.suite_key,
                'workflow_key': result.workflow_key,
                'output_dir': str(result.output_dir),
                'manifest_path': str(result.manifest_path) if result.manifest_path else None,
                'step_count': result.step_count,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-deepprofiler-full-stack':
            config = ProjectConfig.from_json(args.config)
            result = run_deepprofiler_full_stack(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                extra_args=_normalize_extra_args(args.extra_args),
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.delivery',
                'suite_type': 'segmentation',
                'suite_key': result.suite_key,
                'workflow_key': result.workflow_key,
                'output_dir': str(result.output_dir),
                'manifest_path': str(result.manifest_path) if result.manifest_path else None,
                'step_count': result.step_count,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-full-pipeline':
            config = ProjectConfig.from_json(args.config)
            result = run_full_pipeline(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                profiling_suite=args.profiling_suite,
                segmentation_suite=args.segmentation_suite,
                include_validation_report=not args.skip_validation_report,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.full_pipeline',
                'output_dir': str(result.output_dir),
                'profiling_suite': result.profiling_suite,
                'profiling_manifest_path': str(result.profiling_manifest_path) if result.profiling_manifest_path else None,
                'segmentation_suite': result.segmentation_suite,
                'segmentation_manifest_path': str(result.segmentation_manifest_path) if result.segmentation_manifest_path else None,
                'validation_report_path': str(result.validation_report_path) if result.validation_report_path else None,
                'manifest_path': str(result.manifest_path),
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-end-to-end-pipeline':
            config = ProjectConfig.from_json(args.config)
            download_plan = load_download_plan(Path(args.plan_path).expanduser().resolve()) if args.plan_path else None
            should_build_request = bool(download_plan is None and any([
                args.include_data_access_summary,
                args.plan_data_download,
                args.execute_data_download_step,
                args.request_mode != 'gallery-source',
                args.dataset_id is not None,
                args.source_id is not None,
                args.prefix is not None,
                args.subprefix != '',
                args.bucket is not None,
                bool(args.include_substring),
                bool(args.exclude_substring),
                args.max_files is not None,
                args.overwrite,
                args.dry_run,
            ]))
            data_request = None
            if should_build_request:
                data_request = build_data_request(
                    mode=args.request_mode,
                    dataset_id=args.dataset_id,
                    source_id=args.source_id,
                    prefix=args.prefix,
                    subprefix=args.subprefix,
                    bucket=args.bucket,
                    include_substrings=args.include_substring or [],
                    exclude_substrings=args.exclude_substring or [],
                    max_files=args.max_files,
                    overwrite=args.overwrite,
                    dry_run=args.dry_run,
                )
            result = run_end_to_end_pipeline(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                data_request=data_request,
                download_plan=download_plan,
                include_data_access_summary=args.include_data_access_summary,
                plan_data_download=args.plan_data_download,
                execute_data_download_step=args.execute_data_download_step,
                data_summary_max_keys=args.data_summary_max_keys,
                profiling_suite=args.profiling_suite,
                segmentation_suite=args.segmentation_suite,
                run_profiling=not args.skip_profiling,
                run_segmentation=not args.skip_segmentation,
                include_validation_report=not args.skip_validation_report,
                deepprofiler_mode=args.deepprofiler_mode,
            )
            print(json.dumps(end_to_end_pipeline_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'list-pipeline-presets':
            payload = [
                pipeline_preset_definition_to_dict(get_pipeline_preset_definition(key))
                for key in available_pipeline_presets()
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-pipeline-preset':
            config = ProjectConfig.from_json(args.config)
            download_plan = load_download_plan(Path(args.plan_path).expanduser().resolve()) if args.plan_path else None
            should_build_request = bool(download_plan is None and any([
                args.request_mode != 'gallery-source',
                args.dataset_id is not None,
                args.source_id is not None,
                args.prefix is not None,
                args.subprefix != '',
                args.bucket is not None,
                bool(args.include_substring),
                bool(args.exclude_substring),
                args.max_files is not None,
                args.overwrite,
                args.dry_run,
            ]))
            data_request = None
            if should_build_request:
                data_request = build_data_request(
                    mode=args.request_mode,
                    dataset_id=args.dataset_id,
                    source_id=args.source_id,
                    prefix=args.prefix,
                    subprefix=args.subprefix,
                    bucket=args.bucket,
                    include_substrings=args.include_substring or [],
                    exclude_substrings=args.exclude_substring or [],
                    max_files=args.max_files,
                    overwrite=args.overwrite,
                    dry_run=args.dry_run,
                )
            result = run_pipeline_preset(
                config,
                args.preset,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                data_request=data_request,
                download_plan=download_plan,
                profiling_suite=args.profiling_suite,
                segmentation_suite=args.segmentation_suite,
                deepprofiler_mode=args.deepprofiler_mode,
            )
            print(json.dumps(end_to_end_pipeline_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'list-pipeline-skills':
            payload = [
                pipeline_skill_definition_to_dict(get_pipeline_skill_definition(key))
                for key in available_pipeline_skills(include_advanced=args.include_advanced, include_legacy=args.include_legacy)
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-pipeline-skill':
            config = ProjectConfig.from_json(args.config)
            download_plan = load_download_plan(Path(args.plan_path).expanduser().resolve()) if args.plan_path else None
            should_build_request = bool(download_plan is None and any([
                args.request_mode != 'gallery-source',
                args.dataset_id is not None,
                args.source_id is not None,
                args.prefix is not None,
                args.subprefix != '',
                args.bucket is not None,
                bool(args.include_substring),
                bool(args.exclude_substring),
                args.max_files is not None,
                args.overwrite,
                args.dry_run,
            ]))
            data_request = None
            if should_build_request:
                data_request = build_data_request(
                    mode=args.request_mode,
                    dataset_id=args.dataset_id,
                    source_id=args.source_id,
                    prefix=args.prefix,
                    subprefix=args.subprefix,
                    bucket=args.bucket,
                    include_substrings=args.include_substring or [],
                    exclude_substrings=args.exclude_substring or [],
                    max_files=args.max_files,
                    overwrite=args.overwrite,
                    dry_run=args.dry_run,
                )
            result = run_pipeline_skill(
                config,
                args.skill,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                data_request=data_request,
                download_plan=download_plan,
                workflow_root=Path(args.workflow_root).expanduser().resolve() if args.workflow_root else None,
                export_root=Path(args.export_root).expanduser().resolve() if args.export_root else None,
                project_root=Path(args.project_root).expanduser().resolve() if args.project_root else None,
                image_csv_path=Path(args.image_csv_path).expanduser().resolve() if args.image_csv_path else None,
                nuclei_csv_path=Path(args.nuclei_csv_path).expanduser().resolve() if args.nuclei_csv_path else None,
                load_data_csv_path=Path(args.load_data_csv_path).expanduser().resolve() if args.load_data_csv_path else None,
                manifest_path=Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None,
                object_table_path=Path(args.object_table_path).expanduser().resolve() if args.object_table_path else None,
                single_cell_path=Path(args.single_cell_path).expanduser().resolve() if args.single_cell_path else None,
                aggregated_path=Path(args.aggregated_path).expanduser().resolve() if args.aggregated_path else None,
                annotated_path=Path(args.annotated_path).expanduser().resolve() if args.annotated_path else None,
                normalized_path=Path(args.normalized_path).expanduser().resolve() if args.normalized_path else None,
                feature_selected_path=Path(args.feature_selected_path).expanduser().resolve() if args.feature_selected_path else None,
                single_cell_parquet_path=Path(args.single_cell_parquet_path).expanduser().resolve() if args.single_cell_parquet_path else None,
                well_aggregated_parquet_path=Path(args.well_aggregated_parquet_path).expanduser().resolve() if args.well_aggregated_parquet_path else None,
                object_table=args.object_table,
                crop_mode=args.crop_mode,
                workers=args.workers,
                chunk_size=args.chunk_size,
                gpu=args.gpu,
                experiment_name=args.experiment_name,
                config_filename=args.config_filename,
                metadata_filename=args.metadata_filename,
                overwrite=args.overwrite,
            )
            print(json.dumps(pipeline_skill_result_to_dict(result), indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'list-mcp-tools':
            print(json.dumps(mcp_tool_catalog(), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'show-mcp-tool-catalog':
            print(json.dumps(mcp_tool_catalog(), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-mcp-tool':
            params = json.loads(args.params_json)
            if not isinstance(params, dict):
                raise ValueError('--params-json must decode to a JSON object.')
            config = ProjectConfig.from_json(args.config) if args.config else None
            payload = run_mcp_tool_to_dict(
                args.tool,
                config=config,
                **params,
            )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'list-public-api-entrypoints':
            payload = [
                public_api_entrypoint_to_dict(get_public_api_entrypoint(name))
                for name in available_public_api_entrypoints()
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'show-public-api-contract':
            print(json.dumps(public_api_contract_summary(), indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-public-api-entrypoint':
            params = json.loads(args.params_json)
            if not isinstance(params, dict):
                raise ValueError('--params-json must decode to a JSON object.')
            config = ProjectConfig.from_json(args.config) if args.config else None
            payload = run_public_api_entrypoint_to_dict(
                args.entrypoint,
                config=config,
                **params,
            )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'summarize-segmentation':
            config = ProjectConfig.from_json(args.config)
            summary = summarize_segmentation_outputs(config)
            payload = segmentation_summary_to_dict(summary)
            if args.output_path:
                output_path = write_segmentation_summary(summary, Path(args.output_path).expanduser().resolve())
                payload['summary_path'] = str(output_path)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0 if summary.ok else 1

        if args.command == 'collect-validation-report':
            config = ProjectConfig.from_json(args.config)
            report = collect_validation_report(
                config,
                output_path=Path(args.output_path).expanduser().resolve() if args.output_path else None,
            )
            print(json.dumps({
                'implementation': 'native',
                'step': 'collect-validation-report',
                'output_path': str(report.output_path),
                'ok': report.ok,
                'artifact_count': report.artifact_count,
                'ok_count': report.ok_count,
                'missing_count': report.missing_count,
                'failed_count': report.failed_count,
            }, indent=2, ensure_ascii=False))
            return 0 if report.ok else 1

        if args.command == 'serve-mcp':
            run_mcp_server(
                transport=args.transport,
                host=args.host,
                port=args.port,
                path=args.path,
            )
            return 0

        if args.command == 'smoke-test':
            config = ProjectConfig.from_json(args.config)
            result = run_smoke_test(
                config,
                output_path=Path(args.output_path).expanduser().resolve() if args.output_path else None,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.smoke_test',
                'output_path': str(result.output_path),
                'ok': result.ok,
                'check_count': result.check_count,
                'failed_checks': result.failed_checks,
                'validation_ok': result.validation_ok,
            }, indent=2, ensure_ascii=False))
            return 0 if result.ok else 1

        if args.command == 'run-workflow':
            config = ProjectConfig.from_json(args.config)
            workflow_result = run_workflow(
                config,
                args.workflow,
                extra_args=_normalize_extra_args(args.extra_args),
                export_output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
            )
            print(json.dumps({
                'workflow_key': workflow_result.workflow_key,
                'step_count': len(workflow_result.steps),
                'steps': workflow_result.steps,
                'export_root': str(workflow_result.export_root) if workflow_result.export_root else None,
                'manifest_path': str(workflow_result.manifest_path) if workflow_result.manifest_path else None,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'export-deepprofiler-input':
            config = ProjectConfig.from_json(args.config)
            source_kwargs = _resolve_deepprofiler_source_kwargs(args)
            export_result = export_deepprofiler_input(
                config,
                output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
                source_label=args.source_label,
                **source_kwargs,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.deepprofiler_export',
                'export_root': str(export_result.export_root),
                'manifest_path': str(export_result.manifest_path),
                'field_metadata_path': str(export_result.field_metadata_path),
                'locations_root': str(export_result.locations_root),
                'field_count': export_result.field_count,
                'location_file_count': export_result.location_file_count,
                'total_nuclei': export_result.total_nuclei,
                'source_image_csv': str(export_result.source_image_csv),
                'source_nuclei_csv': str(export_result.source_nuclei_csv),
                'source_load_data_csv': str(export_result.source_load_data_csv),
                'source_label': export_result.source_label,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'build-deepprofiler-project':
            config = ProjectConfig.from_json(args.config)
            project_result = build_deepprofiler_project(
                config,
                output_dir=_maybe_resolve_path(args.output_dir),
                workflow_root=_maybe_resolve_path(args.workflow_root),
                export_root=_maybe_resolve_path(args.export_root),
                experiment_name=args.experiment_name,
                config_filename=args.config_name,
                metadata_filename=args.metadata_name,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.deepprofiler_project',
                'project_root': str(project_result.project_root),
                'manifest_path': str(project_result.manifest_path),
                'config_path': str(project_result.config_path),
                'metadata_path': str(project_result.metadata_path),
                'locations_root': str(project_result.locations_root),
                'field_count': project_result.field_count,
                'location_file_count': project_result.location_file_count,
                'image_width': project_result.image_width,
                'image_height': project_result.image_height,
                'image_bits': project_result.image_bits,
                'image_format': project_result.image_format,
                'experiment_name': project_result.experiment_name,
                'label_field': project_result.label_field,
                'control_value': project_result.control_value,
                'export_root': str(project_result.export_root),
                'source_label': project_result.source_label,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-deepprofiler-profile':
            config = ProjectConfig.from_json(args.config)
            profile_result = run_deepprofiler_profile(
                config,
                project_root=Path(args.project_root).expanduser().resolve(),
                experiment_name=args.experiment_name,
                config_filename=args.config_name,
                metadata_filename=args.metadata_name,
                gpu=args.gpu,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.deepprofiler_profile',
                'project_root': str(profile_result.project_root),
                'manifest_path': str(profile_result.manifest_path),
                'config_path': str(profile_result.config_path),
                'metadata_path': str(profile_result.metadata_path),
                'experiment_name': profile_result.experiment_name,
                'feature_dir': str(profile_result.feature_dir),
                'checkpoint_dir': str(profile_result.checkpoint_dir),
                'log_path': str(profile_result.log_path) if profile_result.log_path else None,
                'command': profile_result.command,
                'returncode': profile_result.returncode,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'collect-deepprofiler-features':
            config = ProjectConfig.from_json(args.config)
            collection_result = collect_deepprofiler_features(
                config,
                project_root=Path(args.project_root).expanduser().resolve(),
                output_dir=_maybe_resolve_path(args.output_dir),
                experiment_name=args.experiment_name,
            )
            print(json.dumps({
                'implementation': 'cellpaint_pipeline.deepprofiler_feature_collection',
                'project_root': str(collection_result.project_root),
                'feature_dir': str(collection_result.feature_dir),
                'output_dir': str(collection_result.output_dir),
                'manifest_path': str(collection_result.manifest_path),
                'single_cell_parquet_path': str(collection_result.single_cell_parquet_path),
                'single_cell_csv_gz_path': str(collection_result.single_cell_csv_gz_path),
                'well_aggregated_parquet_path': str(collection_result.well_aggregated_parquet_path),
                'well_aggregated_csv_gz_path': str(collection_result.well_aggregated_csv_gz_path),
                'field_summary_path': str(collection_result.field_summary_path),
                'experiment_name': collection_result.experiment_name,
                'field_file_count': collection_result.field_file_count,
                'cell_count': collection_result.cell_count,
                'feature_count': collection_result.feature_count,
                'metadata_column_count': collection_result.metadata_column_count,
                'well_count': collection_result.well_count,
            }, indent=2, ensure_ascii=False))
            return 0

        if args.command == 'run-deepprofiler-pipeline':
            config = ProjectConfig.from_json(args.config)
            source_kwargs = _resolve_deepprofiler_source_kwargs(args)
            pipeline_result = run_deepprofiler_pipeline(
                config,
                output_dir=_maybe_resolve_path(args.output_dir),
                workflow_root=_maybe_resolve_path(args.workflow_root),
                source_label=args.source_label,
                experiment_name=args.experiment_name,
                config_filename=args.config_name,
                metadata_filename=args.metadata_name,
                gpu=args.gpu,
                **source_kwargs,
            )
            print(json.dumps(deepprofiler_pipeline_result_to_dict(pipeline_result), indent=2, ensure_ascii=False))
            return 0 if pipeline_result.ok else 1

        parser.error(f'Unknown command: {args.command}')
        return 2
    except Exception as exc:
        print(f'[cellpaint_pipeline] error: {exc}')
        return 1


def _resolve_deepprofiler_source_kwargs(args: argparse.Namespace) -> dict[str, Path]:
    source_kwargs: dict[str, Path] = {}
    if args.workflow_root:
        source_kwargs.update(
            infer_deepprofiler_sources_from_workflow_root(
                Path(args.workflow_root).expanduser().resolve()
            )
        )
    if args.image_csv_path:
        source_kwargs['image_csv_path'] = Path(args.image_csv_path).expanduser().resolve()
    if args.nuclei_csv_path:
        source_kwargs['nuclei_csv_path'] = Path(args.nuclei_csv_path).expanduser().resolve()
    if args.load_data_path:
        source_kwargs['load_data_csv_path'] = Path(args.load_data_path).expanduser().resolve()
    return source_kwargs


def _maybe_resolve_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser().resolve()


def _native_result_to_dict(result: object) -> dict:
    if hasattr(result, 'row_count') and hasattr(result, 'unmatched_files'):
        return {
            'implementation': 'native',
            'step': 'build-image-manifest',
            'output_path': str(result.output_path),
            'row_count': result.row_count,
            'unmatched_file_count': len(result.unmatched_files),
            'unmatched_files': result.unmatched_files,
        }
    if hasattr(result, 'feature_selected_path'):
        return {
            'implementation': 'native',
            'step': 'run-pycytominer',
            'aggregated_path': str(result.aggregated_path),
            'annotated_path': str(result.annotated_path),
            'normalized_path': str(result.normalized_path),
            'feature_selected_path': str(result.feature_selected_path),
            'aggregated_row_count': result.aggregated_row_count,
            'aggregated_column_count': result.aggregated_column_count,
            'annotated_row_count': result.annotated_row_count,
            'annotated_column_count': result.annotated_column_count,
            'normalized_row_count': result.normalized_row_count,
            'normalized_column_count': result.normalized_column_count,
            'feature_selected_row_count': result.feature_selected_row_count,
            'feature_selected_column_count': result.feature_selected_column_count,
        }
    if hasattr(result, 'mode'):
        return {
            'implementation': 'native',
            'step': 'export-cellprofiler-to-singlecell',
            'output_path': str(result.output_path),
            'row_count': result.row_count,
            'column_count': result.column_count,
            'object_table': result.object_table,
            'mode': result.mode,
            'shard_count': result.shard_count,
        }
    return {
        'implementation': 'native',
        'step': 'validate-inputs',
        'raw_dir': str(result.raw_dir),
        'raw_file_count': result.raw_file_count,
        'manifest_path': str(result.manifest_path),
        'plate_map_path': str(result.plate_map_path),
        'ok': result.ok,
        'problems': result.problems,
    }


def _native_result_ok(result: object) -> bool:
    if hasattr(result, 'ok'):
        return bool(result.ok)
    if hasattr(result, 'unmatched_files'):
        return len(result.unmatched_files) == 0
    return True


def _native_segmentation_result_to_dict(result: object) -> dict:
    if hasattr(result, 'crop_count') and hasattr(result, 'background_masked'):
        return {
            'implementation': 'native',
            'step': 'extract-single-cell-crops',
            'mode': result.mode,
            'crops_dir': str(result.crops_dir),
            'manifest_path': str(result.manifest_path),
            'crop_count': result.crop_count,
            'worker_count': result.worker_count,
            'background_masked': result.background_masked,
        }
    if hasattr(result, 'preview_count') and hasattr(result, 'manifest_path'):
        return {
            'implementation': 'native',
            'step': 'generate-png-previews',
            'mode': result.mode,
            'manifest_path': str(result.manifest_path),
            'output_dir': str(result.output_dir),
            'preview_count': result.preview_count,
            'worker_count': result.worker_count,
            'chunk_size': result.chunk_size,
        }
    if hasattr(result, 'generated_count'):
        return {
            'implementation': 'native',
            'step': 'generate-sample-previews',
            'output_dir': str(result.output_dir),
            'generated_count': result.generated_count,
            'skipped_existing': result.skipped_existing,
            'field_count': result.field_count,
        }
    if hasattr(result, 'module_count'):
        return {
            'implementation': 'native',
            'step': 'build-mask-export-pipeline',
            'output_path': str(result.output_path),
            'module_count': result.module_count,
            'source_cppipe_path': str(result.source_cppipe_path),
            'selected_via': result.selected_via,
            'execution_mode': result.execution_mode,
        }
    return {
        'implementation': 'native',
        'step': 'prepare-load-data',
        'output_path': str(result.output_path),
        'row_count': result.row_count,
        'plate_count': result.plate_count,
        'well_count': result.well_count,
        'site_count': result.site_count,
    }
